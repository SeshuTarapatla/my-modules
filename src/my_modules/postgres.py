from os import getenv
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

        Constructs a SQLAlchemy-compatible connection string using either:
        1. SQLALCHEMY_CONN_URL environment variable (if set)
        2. Credentials from Kubernetes secrets (as fallback)

        Args:
            database: Name of the database to connect to (default: "postgres")
            local: Whether to connect to localhost instead of the Kubernetes host
                  (default: True on Windows, False otherwise)
            engine: SQLAlchemy dialect engine to use ("psycopg2" or "asyncpg")
                   (default: "psycopg2")

        Returns:
            str: SQLAlchemy connection string in format:
                 "postgresql+engine://user:password@host:port/database"
                 or the value of SQLALCHEMY_CONN_URL environment variable if set

        Raises:
            Exception: If Kubernetes secret retrieval fails or credentials are invalid
                      (only when SQLALCHEMY_CONN_URL is not set)
        """
        if sqlalchemy_conn_url := getenv("SQLALCHEMY_CONN_URL"):
            return sqlalchemy_conn_url
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
    
    def create_db(self) -> bool:
        """Create the database if it doesn't exist.

        Uses the development engine connection to execute a CREATE DATABASE
        statement if the database doesn't already exist.

        Returns:
            bool: True if the database was created or already exists

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If database creation fails due to connection issues,
                                          permission problems, or other database errors
            sqlalchemy.exc.OperationalError: If there are connection or operational issues
            sqlalchemy.exc.ProgrammingError: If there are SQL syntax or permission errors

        Example:
            >>> postgres = Postgres("my_database")
            >>> postgres.create_db()
            True
        """
        if self.db_exists:
            return True

        with self.engine_dev.connect() as conn:
            conn.execute(text(f"CREATE DATABASE {self.database};"))
            conn.commit()
        return True

    def list_db(self) -> list[str]:
        """List all databases in the PostgreSQL instance.

        Retrieves a list of all database names from the pg_database system catalog.

        Returns:
            list[str]: List of database names

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If database listing fails due to connection issues,
                                          permission problems, or query execution errors
            sqlalchemy.exc.OperationalError: If there are connection or operational issues
            sqlalchemy.exc.ProgrammingError: If there are SQL syntax or permission errors

        Example:
            >>> postgres = Postgres()
            >>> postgres.list_db()
            ['postgres', 'template0', 'template1', 'my_database']
        """
        with self.engine_dev.connect() as conn:
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datname NOT LIKE 'template%' ORDER BY datname;"))
            return [row[0] for row in result.fetchall()]

    def drop_db(self, force: bool = False) -> bool:
        """Drop the specified database if it exists.

        Uses the development engine connection to execute a DROP DATABASE
        statement. When force=True, uses FORCE option to terminate all active connections.

        Args:
            force: Whether to forcefully terminate all active connections (default: False)

        Returns:
            bool: True if the database was dropped or didn't exist

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If database dropping fails due to connection issues,
                                          permission problems, active connections (when force=False),
                                          or other database errors
            sqlalchemy.exc.OperationalError: If there are connection or operational issues
            sqlalchemy.exc.ProgrammingError: If there are SQL syntax or permission errors
            sqlalchemy.exc.DatabaseError: If the database is in use and force=False

        Example:
            >>> postgres = Postgres("my_database")
            >>> postgres.drop_db()  # Gentle drop
            True
            >>> postgres.drop_db(force=True)  # Forceful drop
            True
        """
        if not self.db_exists:
            return True

        with self.engine_dev.connect() as conn:
            if force:
                # Use DROP DATABASE WITH (FORCE) to automatically terminate connections
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.database} WITH (FORCE);"))
            else:
                # Gentle drop - may fail if there are active connections
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.database};"))
            conn.commit()
        return True
