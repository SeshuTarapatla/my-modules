from sys import platform
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import Engine, create_engine, text

from my_modules.kubernetes import Kubernetes


class PostgresSecret(BaseModel):
    """Pydantic model representing PostgreSQL connection secrets.

    This class validates and structures PostgreSQL connection credentials
    retrieved from Kubernetes secrets.
    """

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @classmethod
    def get_connection_string(
        cls,
        database: str = "postgres",
        local: bool = (platform == "win32"),
        engine: Literal["psycopg2", "asyncpg"] = "psycopg2",
    ) -> str:
        """Generate a PostgreSQL connection string.

        Constructs a SQLAlchemy-compatible connection string using credentials
        from Kubernetes secrets.

        Args:
            database: Name of the database to connect to (default: "postgres")
            local: Whether to connect to localhost instead of the Kubernetes host
                  (default: True on Windows, False otherwise)
            engine: SQLAlchemy dialect engine to use ("psycopg2" or "asyncpg")
                   (default: "psycopg2")

        Returns:
            str: SQLAlchemy connection string in format:
                 "postgresql+engine://user:password@host:port/database"

        Raises:
            Exception: If Kubernetes secret retrieval fails or credentials are invalid
        """
        k3s_secret = Kubernetes().get_secret("postgres-secret")
        secret = cls(**k3s_secret)
        return f"postgresql+{engine}://{secret.POSTGRES_USER}:{secret.POSTGRES_PASSWORD}@{'localhost' if local else secret.POSTGRES_HOST}:{secret.POSTGRES_PORT}/{database}"


class Postgres:
    """PostgreSQL database connection manager.

    Provides SQLAlchemy engine instances for connecting to PostgreSQL databases.
    Handles both development and production database connections.
    """

    def __init__(self, database: str = "postgres") -> None:
        """Initialize PostgreSQL connection manager.

        Args:
            database: Name of the database to connect to (default: "postgres")
        """
        self.database = database

    @property
    def engine_dev(self) -> Engine:
        """SQLAlchemy engine for development database.

        Creates a connection to the default PostgreSQL database with AUTOCOMMIT
        isolation level, suitable for development and testing.

        Returns:
            Engine: SQLAlchemy engine instance connected to development database

        Note:
            Uses default database name "postgres" and AUTOCOMMIT isolation level
        """
        return create_engine(
            url=PostgresSecret.get_connection_string(), isolation_level="AUTOCOMMIT"
        )

    @property
    def engine(self) -> Engine:
        """SQLAlchemy engine for specified database.

        Creates a connection to the database specified during initialization.

        Returns:
            Engine: SQLAlchemy engine instance connected to the target database

        Note:
            Uses the database name provided in the constructor
        """
        return create_engine(
            url=PostgresSecret.get_connection_string(database=self.database)
        )

    @property
    def db_exists(self) -> bool:
        """Check if the specified database exists in PostgreSQL.

        Executes a query against the pg_database system catalog to verify
        if the database specified during initialization exists.

        Returns:
            bool: True if the database exists, False otherwise

        Note:
            Uses the development engine connection (engine_dev) with AUTOCOMMIT isolation

        Example:
            >>> postgres = Postgres("my_database")
            >>> postgres.db_exists
            True
        """
        with self.engine_dev.connect() as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}';")
            )
            return bool(result.one_or_none())
