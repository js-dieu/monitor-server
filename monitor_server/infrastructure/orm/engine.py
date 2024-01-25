from sqlalchemy import NullPool, create_engine, orm

from monitor_server.infrastructure.orm.config import ORMConfig


class ORMEngine:
    def __init__(self, orm_config: ORMConfig) -> None:
        self._config = orm_config
        self.orm = orm
        self.orm.configure_mappers()
        self.engine = create_engine(orm_config.url, echo=orm_config.echo, poolclass=NullPool)

    @property
    def config(self) -> ORMConfig:
        return self._config

    def __repr__(self) -> str:
        return f'{self._config!r}'

    def _create_session(self) -> orm.Session:
        return self.orm.Session(self.engine)

    @property
    def session(self) -> orm.Session:
        return self._create_session()
