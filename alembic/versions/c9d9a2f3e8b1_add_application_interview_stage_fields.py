"""Add interview stage fields for applications

Revision ID: c9d9a2f3e8b1
Revises: 71fc5bdcd4f7
Create Date: 2026-03-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9d9a2f3e8b1'
down_revision = '71fc5bdcd4f7'
branch_labels = None
depends_on = None


interview_stage_enum = sa.Enum(
    'first_round',
    'second_round',
    'accepted',
    'rejected',
    name='interviewstage'
)


def upgrade() -> None:
    op.add_column(
        'applications',
        sa.Column('current_stage', interview_stage_enum, nullable=False, server_default='first_round', comment='当前面试阶段')
    )
    op.add_column('applications', sa.Column('first_choice_interview_time', sa.String(length=50), nullable=True, comment='第一志愿面试时间'))
    op.add_column('applications', sa.Column('first_choice_interview_location', sa.String(length=100), nullable=True, comment='第一志愿面试地点'))
    op.add_column('applications', sa.Column('second_choice_interview_time', sa.String(length=50), nullable=True, comment='第二志愿面试时间'))
    op.add_column('applications', sa.Column('second_choice_interview_location', sa.String(length=100), nullable=True, comment='第二志愿面试地点'))
    op.add_column('applications', sa.Column('second_round_department', sa.String(length=50), nullable=True, comment='第二轮面试部门'))
    op.add_column('applications', sa.Column('second_round_interview_time', sa.String(length=50), nullable=True, comment='第二轮面试时间'))
    op.add_column('applications', sa.Column('second_round_interview_location', sa.String(length=100), nullable=True, comment='第二轮面试地点'))


def downgrade() -> None:
    op.drop_column('applications', 'second_round_interview_location')
    op.drop_column('applications', 'second_round_interview_time')
    op.drop_column('applications', 'second_round_department')
    op.drop_column('applications', 'second_choice_interview_location')
    op.drop_column('applications', 'second_choice_interview_time')
    op.drop_column('applications', 'first_choice_interview_location')
    op.drop_column('applications', 'first_choice_interview_time')
    op.drop_column('applications', 'current_stage')
