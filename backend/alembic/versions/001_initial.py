"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-06 01:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'roi_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frame_id', sa.BigInteger(), nullable=False),
        sa.Column('x', sa.Integer(), nullable=False),
        sa.Column('y', sa.Integer(), nullable=False),
        sa.Column('w', sa.Integer(), nullable=False),
        sa.Column('h', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roi_events_created_at'), 'roi_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_roi_events_session_id'), 'roi_events', ['session_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_roi_events_session_id'), table_name='roi_events')
    op.drop_index(op.f('ix_roi_events_created_at'), table_name='roi_events')
    op.drop_table('roi_events')
