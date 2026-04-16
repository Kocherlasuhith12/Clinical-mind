"""Initial database migration

Revision ID: 001_initial
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # clinics
    op.create_table(
        'clinics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('district', sa.String(100)),
        sa.Column('state', sa.String(60)),
        sa.Column('lat', sa.Numeric(9, 6)),
        sa.Column('lng', sa.Numeric(9, 6)),
        sa.Column('tier', sa.Enum('phc', 'chc', 'district', name='clinictier'), default='phc'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('role', sa.Enum('doctor', 'asha', 'admin', name='userrole'), nullable=False),
        sa.Column('language', sa.Enum('ta', 'hi', 'en', name='language'), default='en'),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id'), nullable=True),
        sa.Column('password_hash', sa.Text, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # patient_cases
    op.create_table(
        'patient_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('patient_age', sa.SmallInteger),
        sa.Column('patient_sex', sa.Enum('M', 'F', 'O', name='sex_enum')),
        sa.Column('symptoms_text', sa.Text),
        sa.Column('symptoms_language', sa.Enum('ta', 'hi', 'en', name='symlang')),
        sa.Column('symptoms_translated', sa.Text),
        sa.Column('audio_url', sa.Text),
        sa.Column('image_urls', postgresql.ARRAY(sa.Text), default=[]),
        sa.Column('status', sa.Enum('pending', 'processing', 'done', 'urgent', name='casestatus'), default='pending'),
        sa.Column('is_offline', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # diagnoses
    op.create_table(
        'diagnoses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patient_cases.id'), unique=True),
        sa.Column('model_used', sa.String(50)),
        sa.Column('primary_dx', sa.Text),
        sa.Column('differentials', postgresql.JSONB),
        sa.Column('confidence', sa.Numeric(4, 3)),
        sa.Column('is_emergency', sa.Boolean, default=False),
        sa.Column('emergency_reason', sa.Text),
        sa.Column('treatment_plan', sa.Text),
        sa.Column('precautions', sa.Text),
        sa.Column('when_to_refer', sa.Text),
        sa.Column('references', postgresql.JSONB),
        sa.Column('raw_response', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patient_cases.id'), nullable=True),
        sa.Column('action', sa.String(50)),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )

    # sync_queue
    op.create_table(
        'sync_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patient_cases.id')),
        sa.Column('payload', postgresql.JSONB),
        sa.Column('synced', sa.Boolean, default=False),
        sa.Column('retries', sa.SmallInteger, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('synced_at', sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table('sync_queue')
    op.drop_table('audit_logs')
    op.drop_table('diagnoses')
    op.drop_table('patient_cases')
    op.drop_table('users')
    op.drop_table('clinics')
