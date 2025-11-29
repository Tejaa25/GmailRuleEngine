from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from database.models import Base

class DatabaseManager:
    """
    This class is to manage the database connection and sessions.
    """

    def __init__(self):
        """Initialize db manager."""

        self.database_url = Config.get_db_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # Prevent lazy loading issues
        )

    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling."""

        engine = create_engine(self.database_url)
        return engine

    def init_db(self) -> None:
        """Create all database tables."""

        # This is idempotent - safe to run multiple times. - check and remove what it means
        try:
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            raise


# Global database manager instance
db_manager = DatabaseManager()

