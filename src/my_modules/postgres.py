__all__ = ["Postgres"]

from dataclasses import dataclass
from os import getenv
from sys import platform
from typing import cast

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import ProgrammingError

from my_modules.k3s import K3S_Client

POSTGRES_SVC: str = "postgres-service"


@dataclass
class PostgresSecret:
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "postgres"


class Postgres:
    def __init__(self) -> None:
        self.env = cast(PostgresSecret, None)
        self.sql_alchemy_base_url: str = getenv("SQLALCHEMY_CONN_URL") or ""
        if platform == "win32":
            self.env = PostgresSecret(**K3S_Client().get_secret("postgres-secret"))

    def get_connection_string(self, db: str | None = None, host: str | None = None):
        if self.sql_alchemy_base_url:
            return self.sql_alchemy_base_url + f"/{db}"
        db = db if db else self.env.POSTGRES_DB
        host = host if host else self.env.POSTGRES_HOST
        return self.get_base_connection_string(host=host) + f"/{db}"

    def get_base_connection_string(self, host: str = "localhost"):
        if self.sql_alchemy_base_url:
            return self.sql_alchemy_base_url
        host = host if host else self.env.POSTGRES_HOST
        return f"postgresql+psycopg2://{self.env.POSTGRES_USER}:{self.env.POSTGRES_PASSWORD}@{host}:{self.env.POSTGRES_PORT}"

    @property
    def dev_engine(self) -> Engine:
        return create_engine(
            self.get_connection_string(db="postgres"), isolation_level="AUTOCOMMIT"
        )

    def create_db(self, db: str):
        with self.dev_engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{db}";'))

    def db_exists(self, db: str):
        with self.dev_engine.connect() as conn:
            try:
                result = conn.execute(
                    text(f"SELECT datname FROM pg_database WHERE datname = '{db}';")
                )
                return bool(result.first())
            except ProgrammingError:
                return False

    def drop_db(self, db: str):
        with self.dev_engine.connect() as conn:
            conn.execute(text(f'DROP DATABASE "{db}" WITH (FORCE);'))
