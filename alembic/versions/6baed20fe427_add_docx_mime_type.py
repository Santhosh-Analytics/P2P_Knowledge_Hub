"""add docx mime type

Revision ID: 6baed20fe427
Revises: 12d012dbd7bc
Create Date: 2026-08-22 16:00:24.657003

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6baed20fe427"
down_revision: Union[str, Sequence[str], None] = "12d012dbd7bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE mime_type_enum ADD VALUE IF NOT EXISTS 'DOCX'")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
