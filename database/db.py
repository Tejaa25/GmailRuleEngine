from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from config import Config
from database import Base
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """This class is to manage the database connection and sessions."""

    def __init__(self):
        """Initialize db manager."""

        self.database_url = Config.get_db_url()
        self.engine = create_engine(
            self.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def get_session(self):
        """FUnc Usage: Session automatically commits on success or rolls back on exception"""

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def init_db(self) -> None:
        """Create all database tables."""

        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize db: {e}")
            raise

    def health_check(self) -> bool:
        """Check if the db connection is healthy."""

        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session():
    return db_manager.get_session()
