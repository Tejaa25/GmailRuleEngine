import sys

from auth import GmailAuthenticator
from services import GmailClient, EmailStore
from rules.processor import RuleProcessor
from database import db_manager
from config import Config
from utils import parse_arguments
from utils import get_logger

logger = get_logger(__name__)


def setup_database() -> bool:
    """Initialize database schema."""

    try:
        logger.info("Initializing database...")
        db_manager.init_db()
        if db_manager.health_check():  # Health check
            logger.info("Database connection verified")
            return True
        else:
            logger.error("Database health check failed")
            return False
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def fetch_emails_step(gmail_client: GmailClient) -> bool:
    """Fetch and store emails from Gmail."""

    try:
        logger.info("Fetching emails.")
        store = EmailStore(gmail_client)
        success_count, failure_count = store.fetch_and_store()
        logger.info(f"Successfully fetched emails count - {success_count}.")
        if failure_count > 0:
            logger.warning(f"Some emails failed to fetch: {failure_count} failures")
        return True
    except Exception as e:
        logger.error(f"Email fetching failed: {e}")
        return False


def process_rules_step(gmail_client: GmailClient) -> bool:
    """Apply rules to stored emails."""

    try:
        logger.info("Processing rules...")
        processor = RuleProcessor(gmail_client)
        stats = processor.process_emails()
        if stats.actions_failed > 0:
            logger.warning(f"Some actions failed: {stats.actions_failed} failures")
        return True
    except Exception as e:
        logger.error(f"Rule processing failed: {e}")
        return False


def main(fetch_only: bool = False, process_only: bool = False) -> int:
    """Main application workflow."""

    logger.info("-----Gmail Rule Engine Starting-----")

    try:
        Config.validate()
        logger.info("Configuration validated successfully.")
    except Exception as e:
        logger.error(f"Env validation failed - {e}")
        return 1

    try:
        logger.info("Authenticating with Gmail...")
        authenticator = GmailAuthenticator()
        credentials = authenticator.authenticate()
        gmail_client = GmailClient(credentials)
        logger.info("Authentication successful")
    except Exception as e:
        logger.error(f"Gmail authentication failed: {e}")
        return 1

    if not process_only:
        if not fetch_emails_step(gmail_client):
            logger.error("Email fetching step failed. Continuing anyway...")

    if not fetch_only:
        if not process_rules_step(gmail_client):
            logger.error("Rule processing step failed.")
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
    exit_code = main(fetch_only=args.fetch_only, process_only=args.process_only)
    sys.exit(exit_code)
