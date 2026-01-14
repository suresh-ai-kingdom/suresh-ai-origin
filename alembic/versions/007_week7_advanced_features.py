"""Database Alembic Migrations - Week 7 New Models"""

migration_version_007 = """
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Advanced Features
    op.create_table(
        'fine_tune_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('developer_id', sa.String(36), nullable=False),
        sa.Column('base_model', sa.String(100), nullable=False),
        sa.Column('dataset_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), default='queued'),  # queued, training, completed, failed
        sa.Column('progress', sa.Integer, default=0),
        sa.Column('accuracy', sa.Float),
        sa.Column('loss', sa.Float),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
        sa.ForeignKeyConstraint(['developer_id'], ['users.id']),
    )
    
    op.create_table(
        'training_datasets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('developer_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), default='processing'),  # processing, ready, failed
        sa.Column('line_count', sa.Integer),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['developer_id'], ['users.id']),
    )
    
    # Webhooks v2
    op.create_table(
        'webhooks_v2',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('developer_id', sa.String(36), nullable=False),
        sa.Column('url', sa.String(2048), nullable=False),
        sa.Column('secret', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['developer_id'], ['users.id']),
    )
    
    op.create_table(
        'webhook_events_v2',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('webhook_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks_v2.id']),
    )
    
    op.create_table(
        'webhook_deliveries_v2',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('webhook_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('attempt', sa.Integer, default=0),
        sa.Column('response_code', sa.Integer),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('delivered_at', sa.DateTime),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks_v2.id']),
    )
    
    # Custom Prompts Library
    op.create_table(
        'custom_prompts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('template', sa.Text, nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('usage_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    
    # Custom Reports
    op.create_table(
        'custom_reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('config', postgresql.JSON),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    
    # Cohorts
    op.create_table(
        'user_cohorts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('rules', postgresql.JSON),
        sa.Column('size', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )

def downgrade():
    op.drop_table('user_cohorts')
    op.drop_table('custom_reports')
    op.drop_table('custom_prompts')
    op.drop_table('webhook_deliveries_v2')
    op.drop_table('webhook_events_v2')
    op.drop_table('webhooks_v2')
    op.drop_table('training_datasets')
    op.drop_table('fine_tune_jobs')
"""

print("Database migrations ready for Week 7")
print("Run: PYTHONPATH=. alembic upgrade head")
