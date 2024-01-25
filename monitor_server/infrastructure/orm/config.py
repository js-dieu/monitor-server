from pydantic import BaseModel, Field

from monitor_server.infrastructure.config.base import ConfigurationBase


class SessionConfig(BaseModel):
    autoflush: bool = Field(
        default=False,
        description='When True, all query operations will issue a Session.flush() '
        'call to this Session before proceeding.',
    )
    expire_on_commit: bool = Field(
        default=False,
        description='When True, all instances will be fully expired after each commit(), so that all attribute/object'
        ' access subsequent to a completed transaction will load from the most recent database state.',
    )


class ORMConfig(ConfigurationBase, declared_as='orm'):
    driver: str = Field(description='Driver to use for connecting.', default='mysql+mysqldb')
    username: str = Field(description='Username with which to connect to the database server.')
    password: str = Field(description='Password to use for initiating the connection.')
    host: str = Field(description='Hostname for the database server.')
    port: int = Field(description='Port the database server is listening to.')
    echo: bool = Field(default=False, description='Enable sql instructions to be dumped.')
    database: str = Field(description='Name of the server to connect to.', default='')
    session: SessionConfig = Field(description='Session maker configuration')

    def __repr__(self) -> str:
        return f'{self.url}{" ECHOING" if self.echo else ""}'

    @property
    def url(self) -> str:
        if self.database:
            return f'{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
        return f'{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}'
