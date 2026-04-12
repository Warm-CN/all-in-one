"""Add current_stage to signup_configs

Revision ID: f4a6c2b9d1e0
Revises: c9d9a2f3e8b1
Create Date: 2026-03-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4a6c2b9d1e0'
down_revision = 'c9d9a2f3e8b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'signup_configs',
        sa.Column('current_stage', sa.String(length=30), nullable=False, server_default='registration', comment='系统当前阶段')
    )


def downgrade() -> None:
    op.drop_column('signup_configs', 'current_stage')
