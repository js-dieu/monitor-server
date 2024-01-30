"""Add CPU_TYPE to ExecutionContext table

Revision ID: 67466d1fdecf
Revises: b3eb406733c3
Create Date: 2024-01-29 16:55:11.737502

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '67466d1fdecf'
down_revision: str | None = 'b3eb406733c3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('ExecutionContext', sa.Column('cpu_type', sa.String(64), nullable=False))
