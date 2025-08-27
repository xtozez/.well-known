from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.models.lead import LeadStatusEnum

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source', sa.String()),
        sa.Column('campaign', sa.String()),
        sa.Column('channel', sa.String()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('first_name', sa.String()),
        sa.Column('last_name', sa.String()),
        sa.Column('email', sa.String()),
        sa.Column('phone_e164', sa.String()),
        sa.Column('contact_pref', sa.String()),
        sa.Column('consent', sa.Boolean(), server_default='false'),
        sa.Column('message', sa.String()),
        sa.Column('project_type', sa.String()),
        sa.Column('typology', sa.String()),
        sa.Column('budget_min', sa.Float()),
        sa.Column('budget_max', sa.Float()),
        sa.Column('zipcode', sa.String()),
        sa.Column('city', sa.String()),
        sa.Column('origin', sa.String()),
        sa.Column('status', sa.Enum(LeadStatusEnum, name='leadstatusenum'), server_default='Prospect'),
    )
    op.create_index('ix_leads_email', 'leads', ['email'])
    op.create_index('ix_leads_phone', 'leads', ['phone_e164'])
    op.create_index('ix_lead_email_phone', 'leads', ['email', 'phone_e164'])

    op.create_table(
        'properties',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('program', sa.String()),
        sa.Column('lot', sa.String()),
        sa.Column('type', sa.String()),
        sa.Column('area', sa.Float()),
        sa.Column('price', sa.Float()),
        sa.Column('status', sa.String()),
        sa.Column('url_plan', sa.String()),
    )

    op.create_table(
        'interactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lead_id', sa.Integer, sa.ForeignKey('leads.id', ondelete='CASCADE')),
        sa.Column('type', sa.String()),
        sa.Column('content', sa.String()),
        sa.Column('author', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )

    op.create_table(
        'reservations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lead_id', sa.Integer, sa.ForeignKey('leads.id', ondelete='CASCADE')),
        sa.Column('property_id', sa.Integer, sa.ForeignKey('properties.id', ondelete='CASCADE')),
        sa.Column('price', sa.Float()),
        sa.Column('option_date', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('option_expires', sa.DateTime()),
        sa.Column('status', sa.String(), server_default='en_cours'),
    )

    op.create_table(
        'assignments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lead_id', sa.Integer, sa.ForeignKey('leads.id', ondelete='CASCADE')),
        sa.Column('advisor', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lead_id', sa.Integer, sa.ForeignKey('leads.id', ondelete='CASCADE')),
        sa.Column('title', sa.String()),
        sa.Column('due_date', sa.DateTime()),
        sa.Column('owner', sa.String()),
        sa.Column('reminder', sa.DateTime()),
        sa.Column('completed', sa.Boolean(), server_default='false'),
    )

    op.create_table(
        'attachments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lead_id', sa.Integer, sa.ForeignKey('leads.id', ondelete='CASCADE')),
        sa.Column('reservation_id', sa.Integer, sa.ForeignKey('reservations.id', ondelete='CASCADE')),
        sa.Column('filename', sa.String()),
        sa.Column('filetype', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('actor', sa.String()),
        sa.Column('action', sa.String()),
        sa.Column('entity', sa.String()),
        sa.Column('entity_id', sa.Integer),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('payload', sa.JSON()),
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('attachments')
    op.drop_table('tasks')
    op.drop_table('assignments')
    op.drop_table('reservations')
    op.drop_table('interactions')
    op.drop_table('properties')
    op.drop_index('ix_lead_email_phone', table_name='leads')
    op.drop_index('ix_leads_phone', table_name='leads')
    op.drop_index('ix_leads_email', table_name='leads')
    op.drop_table('leads')
