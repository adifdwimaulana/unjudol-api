"""init schema

Revision ID: cf8f7ea30b77
Revises: 
Create Date: 2025-09-06 14:40:07.361137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'cf8f7ea30b77'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create job table
    op.create_table(
        'job',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create comment table
    op.create_table(
        'comment',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], )
    )

    # Create user table
    op.create_table(
        'user',
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('email')
    )

    # Create indexes
    op.create_index('ix_job_action', 'job', ['action'])
    op.create_index('ix_job_type', 'job', ['type'])
    op.create_index('ix_comment_url', 'comment', ['url'])
    op.create_index('ix_comment_label', 'comment', ['label'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_job_action')
    op.drop_index('ix_job_type')
    op.drop_index('ix_comment_url')
    op.drop_index('ix_comment_label')

    # Drop tables
    op.drop_table('user')
    op.drop_table('comment')
    op.drop_table('job')
