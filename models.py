from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
import os
import time

Base = declarative_base()

def get_engine(db_url=None):
    if not db_url:
        db_path = os.getenv('DATA_DB', None)
        if db_path:
            db_url = f"sqlite:///{db_path}"
        else:
            db_url = "sqlite:///data.db"
    return create_engine(db_url, connect_args={"check_same_thread": False})


def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


class Webhook(Base):
    __tablename__ = 'webhooks'
    id = Column(String, primary_key=True)
    event = Column(String, index=True)
    payload = Column(Text)
    received_at = Column(Float)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    amount = Column(Integer)
    currency = Column(String)
    receipt = Column(String)
    product = Column(String, index=True)
    status = Column(String, index=True)
    created_at = Column(Float)
    paid_at = Column(Float, nullable=True)
    payments = relationship('Payment', back_populates='order')


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'), index=True)
    payload = Column(Text)
    received_at = Column(Float)
    order = relationship('Order', back_populates='payments')


class Coupon(Base):
    __tablename__ = 'coupons'
    code = Column(String, primary_key=True, unique=True, index=True)
    discount_percent = Column(Integer)  # 0-100
    description = Column(String, nullable=True)
    expiry_date = Column(Float, nullable=True)  # Unix timestamp or None for no expiry
    max_uses = Column(Integer, nullable=True)  # None for unlimited uses
    current_uses = Column(Integer, default=0)  # Track how many times used
    created_at = Column(Float)
    is_active = Column(Integer, default=1)  # 1=active, 0=inactive


class Customer(Base):
    __tablename__ = 'customers'
    receipt = Column(String, primary_key=True, index=True)  # Unique customer identifier from Razorpay
    segment = Column(String)  # Customer segment: VIP, LOYAL, AT_RISK, etc.
    ltv_paise = Column(Integer)  # Lifetime value in paise
    order_count = Column(Integer, default=0)
    first_purchase_at = Column(Float)
    last_purchase_at = Column(Float)
    last_segmented_at = Column(Float)  # When segment was last calculated


class AbandonedReminder(Base):
    __tablename__ = 'abandoned_reminders'
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'), index=True)
    receipt = Column(String, index=True)
    reminder_sequence = Column(Integer)  # 0=first, 1=second, 2=third
    status = Column(String, default='PENDING')  # PENDING, SENT, OPENED, CLICKED, CONVERTED, BOUNCED, UNSUBSCRIBED
    scheduled_at = Column(Float)  # When reminder is scheduled to send
    sent_at = Column(Float, nullable=True)  # When email was actually sent
    opened_at = Column(Float, nullable=True)  # When email was opened (if tracking)
    clicked_at = Column(Float, nullable=True)  # When link was clicked
    converted_at = Column(Float, nullable=True)  # When order was paid
    created_at = Column(Float)
    email_subject = Column(String, nullable=True)
    discount_offered = Column(Integer, nullable=True)  # Discount % if one was offered


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(String, primary_key=True)  # Razorpay subscription ID or custom ID
    receipt = Column(String, index=True)  # Customer receipt ID
    tier = Column(String, index=True)  # free, pro, scale (supports both Razorpay and Stripe naming)
    billing_cycle = Column(String)  # monthly or yearly
    amount_paise = Column(Integer)  # Subscription amount in paise
    status = Column(String, index=True)  # ACTIVE, PAST_DUE, CANCELLED, EXPIRED, TRIAL
    current_period_start = Column(Float)  # Start of current billing period
    current_period_end = Column(Float)  # End of current billing period
    provider = Column(String, default='razorpay')  # razorpay or stripe
    stripe_subscription_id = Column(String, nullable=True, index=True)  # Stripe subscription ID
    stripe_customer_id = Column(String, nullable=True, index=True)  # Stripe customer ID
    razorpay_subscription_id = Column(String, nullable=True, index=True)  # Razorpay subscription ID
    created_at = Column(Float)
    cancelled_at = Column(Float, nullable=True)  # When subscription was cancelled
    cancellation_reason = Column(String, nullable=True)  # Why customer cancelled


class ReferralProgram(Base):
    __tablename__ = 'referral_programs'
    referral_code = Column(String, primary_key=True)  # Unique referral code
    referrer_receipt = Column(String, index=True, unique=True)  # Who owns this code
    referrer_name = Column(String, nullable=True)  # Referrer's name
    commission_percent = Column(Integer)  # Commission % they earn
    total_referrals = Column(Integer, default=0)  # Total clicks/signups
    successful_referrals = Column(Integer, default=0)  # Paid conversions
    total_commission_paise = Column(Integer, default=0)  # Total earned (all time)
    total_paid_paise = Column(Integer, default=0)  # Total already paid out
    created_at = Column(Float)


class StripeEvent(Base):
    __tablename__ = 'stripe_events'
    id = Column(String, primary_key=True)  # Stripe event ID
    event_type = Column(String, index=True)  # customer.subscription.created, invoice.payment_succeeded, etc.
    payload = Column(Text)  # Full event JSON
    processed = Column(Integer, default=0)  # 1=processed, 0=pending
    processed_at = Column(Float, nullable=True)
    received_at = Column(Float)


class UsageMeter(Base):
    __tablename__ = 'usage_meters'
    id = Column(String, primary_key=True)
    receipt = Column(String, index=True)  # Customer receipt
    subscription_id = Column(String, ForeignKey('subscriptions.id'), index=True)
    attribution_runs = Column(Integer, default=0)  # Runs used this period
    models_used = Column(Integer, default=0)  # # of models accessed
    exports = Column(Integer, default=0)  # # of exports used
    lookback_days = Column(Integer, default=7)  # Lookback window used
    period_start = Column(Float)  # Current billing period start
    period_end = Column(Float)  # Current billing period end
    reset_at = Column(Float)  # Next reset timestamp
    updated_at = Column(Float)


class Referral(Base):
    __tablename__ = 'referrals'
    id = Column(String, primary_key=True)  # Unique referral ID
    referral_code = Column(String, index=True)  # Which code was used
    referrer_receipt = Column(String, index=True)  # Who gets commission
    referred_receipt = Column(String, index=True)  # New customer
    order_id = Column(String, index=True)  # Order from referral
    order_amount_paise = Column(Integer)  # Order value
    commission_percent = Column(Integer)  # Commission % for this referral
    commission_amount_paise = Column(Integer)  # Commission amount
    status = Column(String, index=True)  # PENDING, CONVERTED, PAID, CANCELLED
    converted_at = Column(Float, nullable=True)  # When order was paid
    paid_at = Column(Float, nullable=True)  # When commission was paid
    created_at = Column(Float)


class AIGeneration(Base):
    """Store AI-generated content for tracking and reuse."""
    __tablename__ = 'ai_generations'
    id = Column(String, primary_key=True)
    content_type = Column(String, index=True)  # prompt, email, campaign, product_desc
    prompt = Column(Text)  # What we asked AI to generate
    generated_content = Column(Text)  # What Claude produced
    tokens_used = Column(Integer)  # Token usage for cost tracking
    cost_cents = Column(Integer)  # Cost in cents
    quality_score = Column(Integer)  # 1-100 rating
    user_rating = Column(Integer, nullable=True)  # 1-5 user feedback
    used_count = Column(Integer, default=0)  # Times this was used
    created_at = Column(Float)
    created_by = Column(String)  # receipt/admin who created


class VoiceAnalysis(Base):
    __tablename__ = 'voice_analyses'
    id = Column(String, primary_key=True)
    receipt = Column(String, index=True)
    transcript = Column(Text)
    sentiment_score = Column(Float)  # 0-1
    intents = Column(Text)  # JSON list of intents
    duration_secs = Column(Float, nullable=True)
    analyzed_at = Column(Float)


class AutomationLog(Base):
    __tablename__ = 'automation_logs'
    id = Column(String, primary_key=True)
    workflow_name = Column(String, index=True)
    trigger = Column(String)  # what triggered it
    target_id = Column(String, index=True)  # customer/order/campaign ID
    action_taken = Column(Text)  # JSON description of action
    status = Column(String, index=True)  # SUCCESS, FAILED, SKIPPED
    result = Column(Text, nullable=True)  # outcome details
    executed_at = Column(Float)


class Website(Base):
    __tablename__ = 'websites'
    id = Column(String, primary_key=True)
    product_name = Column(String, index=True)
    product_description = Column(Text)
    target_audience = Column(String)
    industry = Column(String)
    template = Column(String)  # neo_glassmorphism, quantum_grid, etc
    tier = Column(String, index=True)  # BREAKTHROUGH, ELITE, PREMIUM, GROWTH
    tier_color = Column(String)
    performance_score = Column(Integer)  # 0-100
    conversion_lift = Column(Integer)  # percentage
    headline = Column(Text)  # AI-generated headline
    subheader = Column(Text)  # AI-generated subheader
    cta_button = Column(String)  # Call-to-action text
    hero_bg = Column(String)  # CSS gradient
    text_color = Column(String)  # Hex color
    accent_color = Column(String)  # Hex color
    config = Column(Text)  # Full JSON config stored as string
    created_at = Column(Float)
    generated_by = Column(String, nullable=True)  # receipt/admin


class WebsiteMetrics(Base):
    __tablename__ = 'website_metrics'
    id = Column(String, primary_key=True)
    website_id = Column(String, ForeignKey('websites.id'), index=True)
    page_speed = Column(Integer)  # 0-100
    mobile_score = Column(Integer)  # 0-100
    seo_score = Column(Integer)  # 0-100
    accessibility = Column(Integer)  # 0-100
    estimated_conversion_rate = Column(Float)  # 0.01-0.15
    monthly_revenue_impact = Column(String)  # e.g. "+$45,200/month"
    annual_impact = Column(String)  # e.g. "+$542,400/year"
    measured_at = Column(Float)


class WebsiteTemplate(Base):
    __tablename__ = 'website_templates'
    id = Column(String, primary_key=True)
    template_name = Column(String, unique=True)
    tier = Column(String)  # BREAKTHROUGH, ELITE, PREMIUM, GROWTH
    description = Column(Text)
    hero_animation = Column(String)
    sections = Column(Text)  # JSON array of section types
    performance_baseline = Column(Integer)  # Expected base score
    created_at = Column(Float)


class Analytics(Base):
    __tablename__ = 'analytics'
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    visitor_count = Column(Integer)
    active_visitors = Column(Integer)
    total_pageviews = Column(Integer)
    conversion_rate = Column(Float)  # 0-100
    bounce_rate = Column(Float)  # 0-100
    avg_time_on_site = Column(Float)  # seconds
    top_source = Column(String)  # google, facebook, direct, etc
    measured_at = Column(Float)


class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    event_type = Column(String)  # page_view, click, purchase, etc
    page = Column(String, nullable=True)
    event_data = Column(Text, nullable=True)  # JSON
    device = Column(String)  # desktop, mobile, tablet
    source = Column(String)  # traffic source
    recorded_at = Column(Float)


class ConversionFunnel(Base):
    __tablename__ = 'conversion_funnels'
    id = Column(String, primary_key=True)
    funnel_name = Column(String)
    step_name = Column(String)
    step_order = Column(Integer)
    visitor_count = Column(Integer)
    conversion_rate = Column(Float)  # 0-100
    dropoff_rate = Column(Float)  # 0-100
    analyzed_at = Column(Float)


class UserJourney(Base):
    __tablename__ = 'user_journeys'
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    journey_type = Column(String)  # bounce, browser, converter, high_value
    pages_visited = Column(Integer)
    time_on_site = Column(Float)  # seconds
    converted = Column(Integer)  # 0 or 1
    revenue = Column(Float, nullable=True)
    analyzed_at = Column(Float)

# ============================================================================
# FEATURE #18: A/B TESTING ENGINE MODELS
# ============================================================================

class Experiment(Base):
    __tablename__ = 'experiments'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    hypothesis = Column(Text)
    primary_metric = Column(String)  # conversion_rate, revenue_per_visitor, etc.
    status = Column(String, index=True)  # DRAFT, RUNNING, COMPLETED, PAUSED
    confidence_level = Column(Float)  # 0.90, 0.95, 0.99
    min_effect_size = Column(Float)  # minimum detectable effect
    sample_size = Column(Integer)  # target sample size
    winner_variant_id = Column(String, nullable=True)  # winning variant
    created_at = Column(Float)
    started_at = Column(Float, nullable=True)
    ended_at = Column(Float, nullable=True)
    variants = relationship('ExperimentVariant', back_populates='experiment')
    results = relationship('ExperimentResult', back_populates='experiment')


class ExperimentVariant(Base):
    __tablename__ = 'experiment_variants'
    id = Column(String, primary_key=True)
    experiment_id = Column(String, ForeignKey('experiments.id'), index=True)
    variant_name = Column(String)
    description = Column(Text)
    traffic_allocation = Column(Float)  # percentage 0-1
    created_at = Column(Float)
    experiment = relationship('Experiment', back_populates='variants')


class ExperimentResult(Base):
    __tablename__ = 'experiment_results'
    id = Column(String, primary_key=True)
    experiment_id = Column(String, ForeignKey('experiments.id'), index=True)
    variant_id = Column(String, ForeignKey('experiment_variants.id'), index=True)
    visitors = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float)  # 0-100
    revenue = Column(Float, default=0)
    revenue_per_visitor = Column(Float, default=0)
    is_significant = Column(Integer, default=0)  # 0 or 1
    confidence_percent = Column(Float, default=0)  # statistical confidence
    effect_size = Column(Float, default=0)  # % uplift
    recorded_at = Column(Float)
    experiment = relationship('Experiment', back_populates='results')


class JourneyDefinition(Base):
    __tablename__ = 'journey_definitions'
    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    description = Column(Text)
    trigger_type = Column(String)  # signup, cart_abandoned, high_ltv, etc.
    segment = Column(String)  # target segment
    status = Column(String, index=True)  # draft, published, paused, archived
    created_at = Column(Float)
    published_at = Column(Float, nullable=True)
    max_enrollments = Column(Integer, nullable=True)
    enrolled_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    total_value = Column(Float, default=0)
    steps = relationship('JourneyStep', back_populates='journey')
    enrollments = relationship('CustomerJourney', back_populates='journey')


class JourneyStep(Base):
    __tablename__ = 'journey_steps'
    id = Column(String, primary_key=True)
    journey_id = Column(String, ForeignKey('journey_definitions.id'), index=True)
    step_type = Column(String)  # email, sms, wait, decision, push, webhook, action
    position = Column(Integer)
    config = Column(Text)  # JSON config
    created_at = Column(Float)
    journey = relationship('JourneyDefinition', back_populates='steps')
    executions = relationship('JourneyExecution', back_populates='step')


class CustomerJourney(Base):
    __tablename__ = 'customer_journeys'
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    journey_id = Column(String, ForeignKey('journey_definitions.id'), index=True)
    status = Column(String, index=True)  # active, paused, completed
    current_step = Column(Integer, default=0)
    enrolled_at = Column(Float)
    completed_at = Column(Float, nullable=True)
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0)
    engagement_score = Column(Float, default=0)
    customer_data = Column(Text)  # JSON
    journey = relationship('JourneyDefinition', back_populates='enrollments')
    executions = relationship('JourneyExecution', back_populates='enrollment')


class JourneyExecution(Base):
    __tablename__ = 'journey_executions'
    id = Column(String, primary_key=True)
    enrollment_id = Column(String, ForeignKey('customer_journeys.id'), index=True)
    step_id = Column(String, ForeignKey('journey_steps.id'), index=True)
    status = Column(String)  # pending, sent, delivered, opened, clicked, failed, skipped
    result = Column(Text)  # JSON
    executed_at = Column(Float)
    engagement_score = Column(Float, default=0)
    enrollment = relationship('CustomerJourney', back_populates='executions')
    step = relationship('JourneyStep', back_populates='executions')


class TouchpointInteraction(Base):
    __tablename__ = 'touchpoint_interactions'
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    channel = Column(String, index=True)  # email, paid_search, social_media, etc.
    touchpoint_type = Column(String)
    timestamp = Column(Float)
    session_id = Column(String)
    touchpoint_metadata = Column(Text)  # JSON with additional data
    created_at = Column(Float)


class AttributionPath(Base):
    __tablename__ = 'attribution_paths'
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    order_id = Column(String, index=True)
    conversion_value = Column(Float)
    path_length = Column(Integer)
    channels = Column(Text)  # JSON array of channels
    first_touch_channel = Column(String)
    last_touch_channel = Column(String)
    attributed_at = Column(Float)
    created_at = Column(Float)


class ChannelRevenue(Base):
    __tablename__ = 'channel_revenue'
    id = Column(String, primary_key=True)
    channel = Column(String, index=True)
    attribution_model = Column(String)  # first_touch, last_touch, linear, time_decay
    total_attributed_revenue = Column(Float, default=0)
    total_conversions = Column(Integer, default=0)
    total_spend = Column(Float, default=0)
    roi_percent = Column(Float, default=0)
    roas = Column(Float, default=0)
    updated_at = Column(Float)


class AttributionModelData(Base):
    __tablename__ = 'attribution_model_data'
    id = Column(String, primary_key=True)
    order_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    first_touch_credit = Column(Float)
    last_touch_credit = Column(Float)
    linear_credit = Column(Float)
    time_decay_credit = Column(Float)
    model_variance = Column(Float)
    recorded_at = Column(Float)


# ============================================================================
# FEATURE #19: EXECUTION INTELLIGENCE PLATFORM (Week 1 Foundation)
# ============================================================================

class UserProfile(Base):
    """User onboarding profile for execution intelligence platform."""
    __tablename__ = 'user_profiles'
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    goal = Column(String)  # "earn_money", "save_time", "scale_business"
    market = Column(String, index=True)  # "freelancer", "shop_owner", "content_creator", "agency", "student"
    skill_level = Column(String)  # "beginner", "intermediate", "advanced"
    country = Column(String, index=True)  # "IN", "US", "GB", etc
    created_at = Column(Float)
    updated_at = Column(Float)
    executions = relationship('WorkflowExecution', back_populates='user')
    outcomes = relationship('Outcome', back_populates='user')
    recommendations = relationship('Recommendation', back_populates='user')


class WorkflowExecution(Base):
    """Track each time a user executes a workflow (step-by-step guide)."""
    __tablename__ = 'workflow_executions'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('user_profiles.id'), index=True)
    workflow_name = Column(String, index=True)  # "resume_generator", "whatsapp_bot", "prompt_selling"
    status = Column(String, index=True)  # "started", "in_progress", "completed", "abandoned"
    steps_completed = Column(Integer, default=0)  # 1/5, 2/5, 3/5 (user's progress)
    total_steps = Column(Integer, default=5)  # Total steps in workflow
    started_at = Column(Float)
    completed_at = Column(Float, nullable=True)
    execution_notes = Column(Text, nullable=True)  # User's notes during execution
    user = relationship('UserProfile', back_populates='executions')
    outcomes = relationship('Outcome', back_populates='execution')


class Outcome(Base):
    """Capture real-world results from workflow execution."""
    __tablename__ = 'outcomes'
    id = Column(String, primary_key=True)
    execution_id = Column(String, ForeignKey('workflow_executions.id'), index=True)
    user_id = Column(String, ForeignKey('user_profiles.id'), index=True)
    metric_type = Column(String, index=True)  # "revenue", "time_saved", "customers", "custom"
    value = Column(Float)  # ₹5000, 10 hours, 3 customers
    currency = Column(String, default='INR')  # "INR", "USD", "GBP"
    proof_type = Column(String, nullable=True)  # "screenshot", "invoice", "text", "none"
    proof_url = Column(String, nullable=True)  # URL to uploaded proof
    timestamp = Column(Float)
    verified = Column(Integer, default=0)  # 0=pending, 1=verified, -1=rejected
    execution = relationship('WorkflowExecution', back_populates='outcomes')
    user = relationship('UserProfile', back_populates='outcomes')


class WorkflowPerformance(Base):
    """Aggregate metrics: how well does each workflow perform for each segment?"""
    __tablename__ = 'workflow_performance'
    id = Column(String, primary_key=True)
    workflow_name = Column(String, index=True)
    market = Column(String, index=True)  # "freelancer", "shop_owner", etc
    skill_level = Column(String, index=True)  # "beginner", "intermediate", "advanced"
    success_rate = Column(Float, default=0)  # % of users who completed (0-100)
    avg_outcome_value = Column(Float, default=0)  # Average ₹ earned or time saved
    completion_time_hours = Column(Float, default=0)  # Avg hours to complete
    data_points = Column(Integer, default=0)  # How many executions tracked
    updated_at = Column(Float)


class Recommendation(Base):
    """Personalized workflow recommendations for each user."""
    __tablename__ = 'recommendations'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('user_profiles.id'), index=True)
    workflow_name = Column(String, index=True)
    reason = Column(String)  # "73% success rate for your market", "peer recommendation", "matches your goal"
    rank = Column(Integer)  # 1 = top recommendation, 2 = second, etc
    created_at = Column(Float)
    clicked = Column(Integer, default=0)  # 0 or 1
    outcome = Column(String, nullable=True)  # "completed", "abandoned", "in_progress"
    user = relationship('UserProfile', back_populates='recommendations')