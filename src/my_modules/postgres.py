__all__ = ["Postgres"]

from dataclasses import dataclass

from my_modules.k3s import K3S_Client


@dataclass
class PostgresSecret:
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "postgres"


class Postgres:
    def __init__(self) -> None:
        self.env = PostgresSecret(**K3S_Client().get_secret("postgres-secret"))

    def get_connection_string(self, db: str = "", host: str = ""):
        db = db if db else self.env.POSTGRES_DB
        return self.get_base_connection_string() + f"/{db}"

    def get_base_connection_string(self, host: str = ""):
        host = host if host else self.env.POSTGRES_HOST
        return f"postgresql+psycopg2://{self.env.POSTGRES_USER}@{self.env.POSTGRES_PASSWORD}@{host}:{self.env.POSTGRES_PORT}"
