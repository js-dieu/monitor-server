"""Basic support for pytest-monitor metrics

Revision ID: b3eb406733c3
Revises:
Create Date: 2024-01-26 16:36:06.942240
"""

from typing import Sequence

import sqlalchemy as sa
import sqlalchemy.dialects.mysql as mysql
from alembic import op

import monitor_server.application.db.nomenclature as naming

# revision identifiers, used by Alembic.
revision: str = 'b3eb406733c3'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    execution_context = op.create_table(
        'ExecutionContext',
        sa.Column('uid', sa.String(64), nullable=False),
        sa.Column('cpu_frequency', sa.Integer(), nullable=False),
        sa.Column('cpu_vendor', sa.String(256), nullable=False),
        sa.Column('cpu_count', sa.Integer(), nullable=False),
        sa.Column('total_ram', sa.Integer(), nullable=False),
        sa.Column('hostname', sa.String(512), nullable=False),
        sa.Column('machine_type', sa.String(32), nullable=False),
        sa.Column('machine_arch', sa.String(16), nullable=False),
        sa.Column('system_info', sa.String(256), nullable=False),
        sa.Column('python_info', sa.String(512), nullable=False),
        sa.PrimaryKeyConstraint('uid', name=naming.build_primary_key_name('uid')),
    )
    session = op.create_table(
        'Session',
        sa.Column('uid', sa.String(64), nullable=False),
        sa.Column('run_date', mysql.DATETIME(fsp=6), nullable=False),
        sa.Column('scm_id', sa.String(128), nullable=False),
        sa.Column('description', mysql.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('uid', name=naming.build_primary_key_name('uid')),
    )
    op.create_table(
        'TestMetric',
        sa.Column('uid', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('sid', sa.String(64), nullable=False),
        sa.Column('xid', sa.String(64), nullable=False),
        sa.Column('item_start_time', mysql.DATETIME(fsp=6), nullable=False),
        sa.Column('item_path', sa.String(4096), nullable=False),
        sa.Column('item', sa.String(2048), nullable=False),
        sa.Column('variant', sa.String(2048), nullable=False),
        sa.Column('item_fs_loc', sa.String(2048), nullable=False),
        sa.Column('kind', sa.String(64), nullable=False),
        sa.Column('component', sa.String(512), nullable=False),
        sa.Column('wall_time', sa.Float(), nullable=False),
        sa.Column('user_time', sa.Float(), nullable=False),
        sa.Column('kernel_time', sa.Float(), nullable=False),
        sa.Column('cpu_usage', sa.Float(), nullable=False),
        sa.Column('mem_usage', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('uid', name=naming.build_primary_key_name('uid')),
        sa.ForeignKeyConstraint(
            ('sid',),
            refcolumns=[f'{session.name}.uid'],
            name=naming.build_foreign_key_name('TestMetric', 'sid', session.name),
        ),
        sa.ForeignKeyConstraint(
            ('xid',),
            refcolumns=[f'{execution_context.name}.uid'],
            name=naming.build_foreign_key_name('TestMetric', 'sid', execution_context.name),
        ),
    )
