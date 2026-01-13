import os
import json
import time
import hashlib
import smtplib
import ssl
from email.message import EmailMessage
from models import get_engine, get_session, Webhook, Order, Payment, Base
from sqlalchemy.exc import IntegrityError

# Backwards compatible path helper used in some parts of the codebase
def _get_db_path():
    return os.getenv('DATA_DB', os.path.join(os.path.dirname(__file__), 'data.db'))

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')


def _get_db_url():
    """Get database URL with proper fallback to default data.db"""
    db_path = os.getenv('DATA_DB')
    if db_path:
        return f"sqlite:///{db_path}"
    # Default to data.db in current directory
    return f"sqlite:///{DB_PATH}"


def init_db():
    # Initialize models (creates tables if missing)
    engine = get_engine(_get_db_url())
    Base.metadata.create_all(engine)


def save_order(order_id: str, amount: int, currency: str, receipt: str, product: str, status: str = 'created') -> bool:
    init_db()
    session = get_session(get_engine(_get_db_url()))
    o = Order(id=order_id, amount=amount, currency=currency, receipt=receipt, product=product, status=status, created_at=time.time())
    try:
        session.add(o)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()


def get_order(order_id: str):
    session = get_session(get_engine(_get_db_url()))
    row = session.query(Order).filter_by(id=order_id).first()
    session.close()
    if not row:
        return None
    return (row.id, row.amount, row.currency, row.receipt, row.product, row.status, row.created_at, row.paid_at)


def save_payment(payment_id: str, order_id: str, payload: dict) -> bool:
    init_db()
    session = get_session(get_engine(_get_db_url()))
    payload_text = json.dumps(payload)
    p = Payment(id=payment_id, order_id=order_id, payload=payload_text, received_at=time.time())
    try:
        session.add(p)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()


def mark_order_paid(order_id: str, payment_id: str) -> bool:
    init_db()
    session = get_session(get_engine(_get_db_url()))
    row = session.query(Order).filter_by(id=order_id).first()
    updated = False
    if row and row.status != 'paid':
        row.status = 'paid'
        row.paid_at = time.time()
        session.add(row)
        session.commit()
        updated = True
    # ensure payment record exists
    try:
        save_payment(payment_id, order_id, {'payment_id': payment_id})
    except Exception:
        pass
    session.close()
    return updated


def get_payments_by_order(order_id: str):
    session = get_session(get_engine(_get_db_url()))
    rows = session.query(Payment).filter_by(order_id=order_id).all()
    res = [(r.id, r.order_id, r.payload, r.received_at) for r in rows]
    session.close()
    return res


def reconcile_orders():
    """Return a reconciliation report:
    - unpaid_orders: orders with status != 'paid'
    - orphan_payments: payments with no matching order_id
    - candidates: unpaid orders that have at least one payment recorded
    """
    init_db()
    # Switch to ORM-based reconciliation
    session = get_session(get_engine(_get_db_url()))
    unpaid = session.query(Order).filter(Order.status != 'paid').all()
    unpaid_list = [(o.id, o.amount, o.currency, o.receipt, o.product, o.status) for o in unpaid]
    payments = session.query(Payment).all()
    orphans = []
    candidates = []
    all_orders = {o.id for o in session.query(Order.id).all()}
    unpaid_ids = {o.id for o in unpaid}
    for p in payments:
        if not p.order_id or p.order_id not in all_orders:
            orphans.append((p.id, p.order_id, p.payload, p.received_at))
        else:
            if p.order_id in unpaid_ids:
                candidates.append((p.id, p.order_id, p.payload, p.received_at))
    session.close()
    return {'unpaid_orders': unpaid_list, 'orphan_payments': orphans, 'candidates': candidates}


def apply_reconciliation():
    """Apply reconciliation: for each payment that references an unpaid order, mark order as paid and return counts."""
    report = reconcile_orders()
    updated = 0
    for p in report['candidates']:
        pid, oid, payload_text, _ = p
        # mark order paid
        if mark_order_paid(oid, pid):
            updated += 1
    return {'updated_orders': updated, 'candidates': len(report['candidates']), 'orphan_payments': len(report['orphan_payments'])}


def _make_id(payload_text: str) -> str:
    return hashlib.sha256(payload_text.encode()).hexdigest()


def save_webhook(event_id: str, event_name: str, payload: dict) -> bool:
    """Save webhook payload. Returns True if inserted, False if already existed."""
    init_db()
    session = get_session(get_engine(_get_db_url()))
    payload_text = json.dumps(payload)
    wh = Webhook(id=event_id, event=event_name, payload=payload_text, received_at=time.time())
    try:
        session.add(wh)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()


def get_webhook_by_id(event_id: str):
    session = get_session(get_engine(_get_db_url()))
    row = session.query(Webhook).filter_by(id=event_id).first()
    session.close()
    if not row:
        return None
    return (row.id, row.event, row.payload, row.received_at)


def send_email(subject: str, body: str, to_addr: str, html_body: str = None):
    """Send email with optional HTML body.
    
    Args:
        subject: Email subject line
        body: Plain text body (fallback)
        to_addr: Recipient email address
        html_body: Optional HTML formatted body
    """
    user = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    if not user or not password:
        raise RuntimeError('Email credentials not configured')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to_addr
    msg.set_content(body)
    
    # Add HTML alternative if provided
    if html_body:
        msg.add_alternative(html_body, subtype='html')
    
    context = ssl.create_default_context()
    # Using SMTP_SSL by default; tests can monkeypatch smtplib.SMTP_SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
    return True
