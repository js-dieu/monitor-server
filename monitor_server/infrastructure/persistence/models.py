import typing as t
from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from monitor_server.domain.models.machines import Machine
from monitor_server.infrastructure.orm.declarative import ORMModel


class Session(ORMModel):
    uid: Mapped[UUID] = mapped_column(nullable=False, primary_key=True)
    run_date: Mapped[datetime] = mapped_column(nullable=False)
    description: Mapped[t.Dict[str, t.Any]] = mapped_column(MutableDict.as_mutable(JSON()), nullable=False)
    scm_id: Mapped[str] = mapped_column(String(128), nullable=False)


class ExecutionContext(ORMModel):
    uid: Mapped[UUID] = mapped_column(nullable=False, primary_key=True)
    cpu_frequency: Mapped[int] = mapped_column(Integer(), nullable=False)
    cpu_vendor: Mapped[str] = mapped_column(String(256), nullable=False)
    cpu_count: Mapped[int] = mapped_column(Integer(), nullable=False)
    cpu_type: Mapped[str] = mapped_column(String(64), nullable=False)
    total_ram: Mapped[int] = mapped_column(Integer(), nullable=False)
    hostname: Mapped[str] = mapped_column(String(512), nullable=False)
    machine_type: Mapped[str] = mapped_column(String(32), nullable=False)
    machine_arch: Mapped[str] = mapped_column(String(16), nullable=False)
    system_info: Mapped[str] = mapped_column(String(256), nullable=False)
    python_info: Mapped[str] = mapped_column(String(512), nullable=False)

    @classmethod
    def from_dict(cls, data: t.Dict[str, t.Any]) -> 'ExecutionContext':
        return cls(
            uid=data.get('footprint', data['uid']),
            cpu_frequency=data['cpu_frequency'],
            cpu_vendor=data['cpu_vendor'],
            cpu_count=data['cpu_count'],
            cpu_type=data['cpu_type'],
            total_ram=data['total_ram'],
            hostname=data['hostname'],
            machine_type=data['machine_type'],
            machine_arch=data['machine_arch'],
            system_info=data['system_info'],
            python_info=data['python_info'],
        )

    @classmethod
    def from_model(cls, value: Machine) -> 'ExecutionContext':
        return cls(
            uid=value.uid,
            cpu_frequency=value.cpu_frequency,
            cpu_vendor=value.cpu_vendor,
            cpu_count=value.cpu_count,
            cpu_type=value.cpu_type,
            total_ram=value.total_ram,
            hostname=value.hostname,
            machine_type=value.machine_type,
            machine_arch=value.machine_arch,
            system_info=value.system_info,
            python_info=value.python_info,
        )


class TestMetric(ORMModel):
    uid: Mapped[UUID] = mapped_column(nullable=False, primary_key=True)
    sid: Mapped[str] = mapped_column(String(64), ForeignKey(Session.uid), nullable=False)
    xid: Mapped[str] = mapped_column(String(64), ForeignKey(ExecutionContext.uid), nullable=False)
    item_start_time: Mapped[datetime] = mapped_column(nullable=False)
    item_path: Mapped[str] = mapped_column(String(4096), nullable=False)
    item: Mapped[str] = mapped_column(String(2048), nullable=False)
    variant: Mapped[str] = mapped_column(String(2048), nullable=False)
    item_fs_loc: Mapped[str] = mapped_column(String(2048), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    component: Mapped[str] = mapped_column(String(512), nullable=False)
    wall_time: Mapped[float] = mapped_column(Float(), nullable=False)
    user_time: Mapped[float] = mapped_column(Float(), nullable=False)
    kernel_time: Mapped[float] = mapped_column(Float(), nullable=False)
    cpu_usage: Mapped[float] = mapped_column(Float(), nullable=False)
    mem_usage: Mapped[float] = mapped_column(Float(), nullable=False)
    session = relationship(Session)
    execution_context = relationship(ExecutionContext)
