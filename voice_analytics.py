import time
import json
import uuid
from typing import Dict, List, Tuple
from models import get_engine, get_session, VoiceAnalysis
from utils import _get_db_url, init_db

POSITIVE_WORDS = {
    'great', 'good', 'love', 'amazing', 'happy', 'awesome', 'excellent', 'fast', 'helpful'
}
NEGATIVE_WORDS = {
    'bad', 'issue', 'problem', 'hate', 'angry', 'slow', 'bug', 'refund', 'broken', 'confused'
}
INTENT_KEYWORDS = {
    'REFUND': ['refund', 'money back', 'cancel'],
    'UPGRADE': ['upgrade', 'pro', 'premium'],
    'DISCOUNT': ['discount', 'offer', 'coupon'],
    'SUPPORT': ['help', 'support', 'issue', 'problem', 'bug'],
    'FEEDBACK': ['feedback', 'suggestion', 'idea'],
}


def _score_sentiment(text: str) -> float:
    words = [w.strip('.,!?').lower() for w in text.split()] if text else []
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = max(pos + neg, 1)
    # scale to 0..1, bias towards neutral 0.5
    raw = (pos - neg) / total
    score = max(0.0, min(1.0, 0.5 + raw * 0.5))
    return round(score, 3)


def _detect_intents(text: str) -> List[str]:
    t = text.lower() if text else ''
    intents = []
    for intent, kws in INTENT_KEYWORDS.items():
        if any(k in t for k in kws):
            intents.append(intent)
    if not intents:
        intents.append('GENERAL')
    return intents


def analyze_transcript(payload: Dict) -> Dict:
    """Analyze transcript payload for sentiment and intents.
    Payload may include: transcript (str), receipt (str), duration_secs (float), agent_talk_secs, customer_talk_secs.
    """
    transcript = payload.get('transcript', '')
    receipt = payload.get('receipt')
    duration_secs = payload.get('duration_secs')
    sentiment = _score_sentiment(transcript)
    intents = _detect_intents(transcript)
    # optional talk ratio
    agent = float(payload.get('agent_talk_secs') or 0)
    customer = float(payload.get('customer_talk_secs') or 0)
    talk_ratio = None
    if agent + customer > 0:
        talk_ratio = round(customer / (agent + customer), 3)
    return {
        'receipt': receipt,
        'transcript': transcript,
        'duration_secs': duration_secs,
        'sentiment_score': sentiment,
        'intents': intents,
        'talk_ratio_customer': talk_ratio,
        'analyzed_at': time.time(),
    }


def save_analysis(result: Dict) -> str:
    init_db()
    session = get_session(get_engine(_get_db_url()))
    vid = str(uuid.uuid4())
    row = VoiceAnalysis(
        id=vid,
        receipt=result.get('receipt'),
        transcript=result.get('transcript'),
        sentiment_score=float(result.get('sentiment_score') or 0),
        intents=json.dumps(result.get('intents') or []),
        duration_secs=float(result.get('duration_secs') or 0) if result.get('duration_secs') is not None else None,
        analyzed_at=float(result.get('analyzed_at') or time.time()),
    )
    session.add(row)
    session.commit()
    session.close()
    return vid


def list_analyses(days_back: int = 90) -> List[Dict]:
    init_db()
    session = get_session(get_engine(_get_db_url()))
    since = time.time() - days_back * 86400.0
    rows = session.query(VoiceAnalysis).filter(VoiceAnalysis.analyzed_at >= since).order_by(VoiceAnalysis.analyzed_at.desc()).all()
    out: List[Dict] = []
    for r in rows:
        out.append({
            'id': r.id,
            'receipt': r.receipt,
            'sentiment_score': r.sentiment_score,
            'intents': json.loads(r.intents or '[]'),
            'duration_secs': r.duration_secs,
            'analyzed_at': r.analyzed_at,
        })
    session.close()
    return out


def aggregate_metrics(days_back: int = 90) -> Dict:
    items = list_analyses(days_back)
    n = len(items)
    avg_sentiment = round(sum(i['sentiment_score'] for i in items) / max(n, 1), 3)
    intent_counts: Dict[str, int] = {}
    for i in items:
        for intent in i['intents']:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
    top_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    avg_duration = round(sum((i['duration_secs'] or 0) for i in items) / max(n, 1), 2)
    return {
        'count': n,
        'avg_sentiment': avg_sentiment,
        'avg_duration_secs': avg_duration,
        'top_intents': top_intents,
        'generated_at': time.time(),
    }
