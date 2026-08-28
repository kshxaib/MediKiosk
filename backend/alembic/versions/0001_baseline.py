"""baseline — foundation, no tables

Revision ID: 0001_baseline
Revises:
Create Date: 2026-08-28

Phase 1 foundation baseline. This migration intentionally creates NO tables:
it establishes the Alembic version chain so that the first business models
(introduced from Phase 2 onward) have a parent revision to build on.
"""
from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: no schema in Phase 1."""
    pass


def downgrade() -> None:
    """No-op: no schema in Phase 1."""
    pass
