"""Cascading delete

Revision ID: c145aced177c
Revises: 67466d1fdecf
Create Date: 2024-02-01 16:53:21.034137

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

import monitor_server.application.db.nomenclature as naming

# revision identifiers, used by Alembic.
revision: str = 'c145aced177c'
down_revision: str | None = '67466d1fdecf'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column('TestMetric', 'uid', type_=sa.String(32), nullable=False)
    op.drop_constraint(
        constraint_name=naming.build_foreign_key_name('TestMetric', 'sid', 'ExecutionContext'),
        table_name='TestMetric',
        type_='foreignkey',
    )
    op.create_foreign_key(
        constraint_name=naming.build_foreign_key_name('TestMetric', 'xid', 'ExecutionContext'),
        source_table='TestMetric',
        referent_table='ExecutionContext',
        local_cols=['xid'],
        remote_cols=['uid'],
        ondelete='CASCADE',
    )
    op.drop_constraint(
        constraint_name=naming.build_foreign_key_name('TestMetric', 'sid', 'Session'),
        table_name='TestMetric',
        type_='foreignkey',
    )
    op.create_foreign_key(
        constraint_name=naming.build_foreign_key_name('TestMetric', 'sid', 'Session'),
        source_table='TestMetric',
        referent_table='Session',
        local_cols=['sid'],
        remote_cols=['uid'],
        ondelete='CASCADE',
    )
