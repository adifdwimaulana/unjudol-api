"""add unique constraint in job url action

Revision ID: cb288ca3f747
Revises: cf8f7ea30b77
Create Date: 2025-09-09 02:17:18.559834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb288ca3f747'
down_revision: Union[str, Sequence[str], None] = 'cf8f7ea30b77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_job_url_action", "job", ["url", "action"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_job_url_action", "job", type_="unique")
