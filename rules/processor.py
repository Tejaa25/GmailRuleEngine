from dataclasses import dataclass

from database import Email
from database import get_db_session
from services import GmailClient
from rules import RuleLoader
from actions import get_action
from config import Config
from utils import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for rule processing."""

    emails_processed: int = 0
    emails_matched: int = 0
    actions_executed: int = 0
    actions_successful: int = 0
    actions_failed: int = 0

    def __str__(self) -> str:
        return (
            f"Processed: {self.emails_processed} emails\n"
            f"Matched: {self.emails_matched} emails\n"
            f"Executed actions: {self.actions_executed}\n"
            f"Success actions: {self.actions_successful}\n"
            f"Failed actions: {self.actions_failed}\n"
        )


class RuleProcessor:
    """This class is to process the emails according to the rules."""

    def __init__(self, gmail_client: GmailClient):
        self.gmail_client = gmail_client
        self.rules = RuleLoader(gmail_client=gmail_client).load_rules()
        self.stats = ProcessingStats()

    def process_emails(self):

        if not self.rules:
            logger.warning("No rules configured")
            return self.stats
        # Process in batches
        with get_db_session() as session:
            query = session.query(Email).filter(Email.processed == False)
            emails = query.limit(Config.RULE_PROCESSING_BATCH_SIZE).all()

            logger.info(f"Found {len(emails)} emails to process")

            for email in emails:
                self._process_single_email(email)
            session.commit()

        logger.info(f"Processing complete:\n{self.stats}")
        return self.stats

    def _process_single_email(self, email: Email) -> None:
        """Process a single email with al rules."""

        self.stats.emails_processed += 1
        matched_any_rule = False
        try:
            for rule in self.rules:
                if rule.matches(email):
                    matched_any_rule = True
                    logger.info(
                        f"Email {email.id[:10]}... matched rule: {rule.description}"
                    )
                    for action_dict in rule.actions: # Execute actions
                        self._execute_action(email, action_dict)
            if matched_any_rule:
                self.stats.emails_matched += 1
            email.processed = True
        except Exception as e:
            logger.error(f"Error processing email {email.id}: {e}")

    def _execute_action(self, email: Email, action_dict: dict) -> None:
        """Execute a single action on an email."""

        action_name = action_dict.get("action")
        self.stats.actions_executed += 1
        # Get action executor
        action_func = get_action(action_name)
        if not action_func:
            logger.error(f"Unknown action: {action_name}")
            self.stats.actions_failed += 1
            return
        # Execute action
        try:
            success = action_func(self.gmail_client, email, action_dict)
            if success:
                self.stats.actions_successful += 1
            else:
                self.stats.actions_failed += 1
        except Exception as e:
            logger.error(f"Action '{action_name}' failed for email {email.id}: {e}")
            self.stats.actions_failed += 1
