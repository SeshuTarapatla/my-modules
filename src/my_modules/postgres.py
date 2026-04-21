import tarfile
from os import getenv
from pathlib import Path
from sys import platform
from tempfile import TemporaryDirectory
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.exc import OperationalError

from my_modules.datetime_utils import Timestamp
from my_modules.kubernetes import Kubernetes
from my_modules.logger import get_logger

# Logger instance for PostgreSQL operations
log = get_logger(__name__)

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
        self._engine = None
        self._engine_dev = None

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
        self._engine_dev = self._engine_dev or create_engine(
            url=PostgresSecret.get_connection_string(), isolation_level="AUTOCOMMIT"
        )
        return self._engine_dev

    @property
    def engine(self) -> Engine:
        """SQLAlchemy engine for specified database.

        Creates a connection to the database specified during initialization.

        Returns:
            Engine: SQLAlchemy engine instance connected to the target database

        Note:
            Uses the database name provided in the constructor
        """
        self._engine = self._engine or create_engine(
            url=PostgresSecret.get_connection_string(database=self.database)
        )
        return self._engine

    @property
    def exists(self) -> bool:
        """Check if the specified database exists in PostgreSQL.

        Executes a query against the pg_database system catalog to verify
        if the database specified during initialization exists.

        Returns:
            bool: True if the database exists, False otherwise

        Note:
            Uses the development engine connection (engine_dev) with AUTOCOMMIT isolation
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
        """
        # Check if database exists using the target database name
        with self.engine_dev.connect() as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}';")
            )
            if result.one_or_none():
                return True

            conn.execute(text(f"CREATE DATABASE {self.database};"))
            conn.commit()
        return True

    def drop_db(self, force: bool = False) -> bool:
        """Drop the specified database if it exists.

        Uses the development engine connection to execute a DROP DATABASE
        statement. When force=True, uses FORCE option to terminate all active connections.

        Args:
            force: Whether to forcefully terminate all active connections (default: False)

        Returns:
            bool: True if the database was dropped or didn't exist
        """
        # Prevent dropping the default postgres database
        if self.database == "postgres":
            raise ValueError("Cannot drop the 'postgres' database. It's a read-only system database.")

        # Check if database exists using the target database name
        with self.engine_dev.connect() as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}';")
            )
            if not result.one_or_none():
                return True

            if force:
                # Use DROP DATABASE WITH (FORCE) to automatically terminate connections
                conn.execute(
                    text(f"DROP DATABASE IF EXISTS {self.database} WITH (FORCE);")
                )
            else:
                # Gentle drop - may fail if there are active connections
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.database};"))
            conn.commit()
        return True

    def list_db(self) -> list[str]:
        """List all databases in the PostgreSQL instance.

        Retrieves a list of all database names from the pg_database system catalog.
        Excludes template databases which are used for creating new databases.

        Returns:
            list[str]: List of database names (excluding template databases)
        """
        with self.engine_dev.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT datname FROM pg_database WHERE datname NOT LIKE 'template%' ORDER BY datname;"
                )
            )
            return [row[0] for row in result.fetchall()]

    def list_tables(self) -> list[str]:
        """List all tables in the current database.

        Returns a list of table names that exist in the current database.
        Raises OperationalError if the database doesn't exist.

        Returns:
            list[str]: List of table names in the database

        Raises:
            OperationalError: If the database doesn't exist
        """
        if self.database not in self.list_db():
            raise OperationalError(
                statement=f"Database '{self.database}' does not exist.",
                params=None,
                orig=Exception(
                    f"Database '{self.database}' does not exist in PostgreSQL instance."
                ),
            )
        return inspect(self.engine).get_table_names()

    def _get_sorted_tables(self) -> list[str]:
        """Return tables sorted by FK dependencies (parents before children).

        Uses topological sorting to order tables such that parent tables (those referenced by FKs)
        are processed before child tables (those with FKs referencing other tables).
        This is critical for proper database backup/restore operations.

        Returns:
            list[str]: Tables sorted by foreign key dependencies
        """
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        dependencies: dict[str, set[str]] = {table: set() for table in tables}

        for table in tables:
            for fk in inspector.get_foreign_keys(table):
                referred = fk["referred_table"]
                if referred in dependencies and referred != table:
                    dependencies[table].add(referred)

        sorted_tables = []
        visited = set()

        def visit(table: str) -> None:
            """Recursive helper function for topological sort."""
            if table in visited:
                return
            visited.add(table)
            for dep in dependencies[table]:
                visit(dep)
            sorted_tables.append(table)

        for table in tables:
            visit(table)

        return sorted_tables

    def backup_db(self) -> Path:
        """Create a compressed backup of the database with all tables.

        Creates a tar.gz archive containing CSV dumps of all tables, sorted by FK dependencies.
        Includes a manifest file to preserve the table order for restoration.

        Returns:
            Path: Path to the created backup archive

        Raises:
            OperationalError: If the database has no tables to backup
        """
        tables = self._get_sorted_tables()
        if not tables:
            raise OperationalError(
                statement=f"Database '{self.database}' has no tables to backup.",
                params=None,
                orig=Exception(
                    f"Database '{self.database}' has zero tables in PostgreSQL instance."
                ),
            )
        total = len(tables)
        timestamp = Timestamp()
        archive = Path(
            f"{self.database}_backup_{timestamp.strftime('underscore')}.tar.gz"
        )
        log.info(f"PostgreSQL Database Backup: [bold blue]{self.database}[/]")
        log.info(f"Metadata: {timestamp} | Tables: {total}")

        # Create backup using raw SQL connection for optimal performance
        with self.engine.raw_connection() as conn:
            cur = conn.cursor()
            with TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                with tarfile.open(archive, "w:gz") as tar:
                    # Export tables to CSV files and add to archive
                    for i, table in enumerate(tables, start=1):
                        log.info(f"Exporting table {i}/{total}: [green]{table}")
                        csv_path = tmpdir_path / f"{table}.csv"
                        with csv_path.open("w", encoding="utf-8") as f:
                            cur.copy_expert(
                                f'COPY "{table}" TO STDOUT WITH CSV HEADER;',
                                f,
                            )
                        tar.add(csv_path, arcname=csv_path.name)

                    # Save FK order as a manifest so restore doesn't need to recompute it
                    manifest_path = tmpdir_path / "_manifest.txt"
                    manifest_path.write_text("\n".join(tables), encoding="utf-8")
                    tar.add(manifest_path, arcname=manifest_path.name)

        log.info(f"Backup exported to [blue]{archive.absolute()}[/]")
        return archive

    def restore_db(self, archive: Path) -> bool:
        """Restore database from a backup archive.

        Extracts CSV files from the backup archive and imports them into the database.
        Handles foreign key constraints properly by using the manifest order if available.

        Args:
            archive: Path to the backup archive file

        Returns:
            bool: True if restore was successful

        Raises:
            FileNotFoundError: If backup archive doesn't exist
            OperationalError: If required tables are missing from the database
        """
        if not archive.exists():
            raise FileNotFoundError(f"Backup archive not found: {archive}")

        existing_tables = set(self.list_tables())

        log.info(f"PostgreSQL Database Restore: [bold blue]{self.database}[/]")
        log.info(f"Restoring from [cyan]{archive.absolute()}[/]")

        # Use raw SQL connection for better performance with bulk operations
        with self.engine.raw_connection() as conn:
            cur = conn.cursor()
            with TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                with tarfile.open(archive, "r:gz") as tar:
                    tar.extractall(tmpdir_path)

                # Prefer manifest order, fall back to FK-sorted live introspection
                manifest_path = tmpdir_path / "_manifest.txt"
                if manifest_path.exists():
                    ordered_tables = [
                        t for t in manifest_path.read_text(encoding="utf-8").splitlines()
                        if t.strip()
                    ]
                    log.info("Using manifest order from archive for restoration.")
                else:
                    ordered_tables = self._get_sorted_tables()
                    log.warning("No manifest found in archive, falling back to live FK sort.")

                # Validate all tables exist before touching anything
                csv_files = {p.stem: p for p in tmpdir_path.glob("*.csv")}
                missing = [t for t in ordered_tables if t not in existing_tables]
                if missing:
                    raise OperationalError(
                        statement=f"Tables missing in '{self.database}': {missing}",
                        params=None,
                        orig=Exception(
                            f"Cannot restore: tables {missing} not found. Ensure schema is applied first."
                        ),
                    )

                total = len(ordered_tables)
                log.info(f"Tables to restore: {total}")

                # Disable FK checks, truncate in reverse order, restore in forward order
                cur.execute("SET session_replication_role = 'replica';")
                try:
                    # Truncate tables in reverse order to handle dependencies
                    for table in reversed(ordered_tables):
                        if table in csv_files:
                            log.info(f"Truncating: [yellow]{table}")
                            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")

                    # Restore data in forward order (FK dependencies first)
                    for i, table in enumerate(ordered_tables, start=1):
                        if table not in csv_files:
                            log.warning(f"Skipping table {i}/{total}: [yellow]{table}[/] (no CSV in archive)")
                            continue
                        log.info(f"Importing table {i}/{total}: [green]{table}")
                        with csv_files[table].open("r", encoding="utf-8") as f:
                            cur.copy_expert(
                                f"COPY {table} FROM STDIN WITH CSV HEADER;",
                                f,
                            )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    cur.execute("SET session_replication_role = 'origin';")
                    conn.commit()

        log.info(f"Restore complete for [bold blue]{self.database}[/]")
        return True