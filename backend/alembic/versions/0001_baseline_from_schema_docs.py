"""baseline migration placeholder from documented schema

Revision ID: 0001_baseline
Revises:
Create Date: 2026-02-20
"""

from pathlib import Path
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    root = Path(__file__).resolve().parents[3]
    schema_file = root / "docs" / "db" / "schema_v1.sql"
    op.execute(schema_file.read_text(encoding="utf-8"))


def downgrade() -> None:
    raise NotImplementedError("Downgrade is not implemented for baseline schema migration.")
