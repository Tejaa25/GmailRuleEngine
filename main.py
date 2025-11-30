import sys

from auth import GmailAuthenticator
from services.gmail_client import GmailClient
from database import db_manager
from config import Config
from utils import parse_arguments
from utils.logger import get_logger

logger = get_logger(__name__)


def setup_database() -> bool:
    """Initialize database schema."""

    try:
        logger.info("Initializing database...")
        db_manager.init_db()
        if db_manager.health_check(): # Health check
            logger.info("Database connection verified")
            return True
        else:
            logger.error("Database health check failed")
            return False
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def main() -> int:
    """Main application workflow."""

    logger.info("-----Gmail Rule Engine Starting-----")

    try:
        Config.validate()
        logger.info("Configuration validated successfully.")
    except Exception as e:
        logger.error("Env validation failed.")
        return 1

    try:
        logger.info("Authenticating with Gmail...")
        authenticator = GmailAuthenticator()
        credentials = authenticator.authenticate()
        GmailClient(credentials)
        logger.info("Authentication successful")
    except Exception as e:
        logger.error(f"Gmail authentication failed: {e}")
        return 1

    logger.info("-----Gmail Rule Engine Completed Successfully-----")
    return 0


if __name__ == "__main__":
    args = parse_arguments()

    # just initialize database
    db_setup_status = setup_database()
    if args.init_db:
        if db_setup_status:
            logger.info("Database initialized successfully")
            sys.exit(0)
        else:
            logger.error("Database initialization failed")
            sys.exit(1)

    # Run main func
    exit_code = main()
    sys.exit(exit_code)
