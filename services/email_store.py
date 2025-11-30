from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from services import GmailClient
from database import Email
from database import get_db_session
from config import Config
from utils import get_logger

logger = get_logger(__name__)


class EmailStore:
    """Service for fetching and storing emails."""

    def __init__(self, gmail_client: GmailClient):
        self.gmail_client = gmail_client

    def fetch_and_store(self):
        """Fetch emails from Gmail and store in database."""

        success_count = 0
        failure_count = 0
        logger.info(f"Fetching emails.")

        # Get the message IDs
        message_refs = self.gmail_client.list_messages()
        if not message_refs:
            logger.info("No messages found")
            return success_count, failure_count

        logger.info(f"Found {len(message_refs)} messages to process")
        with get_db_session() as session:
            # TODO: We can optimize this by fetching messages in parallel
            # but keeping it simple for now
            for i in range(0, len(message_refs), Config.FETCH_BATCH_SIZE):
                batch = message_refs[i : i + Config.FETCH_BATCH_SIZE]
                batch_success, batch_fail = self._process_batch(session, batch)
                success_count += batch_success
                failure_count += batch_fail
                logger.info(
                    f"Batch {i//Config.FETCH_BATCH_SIZE + 1}: "
                    f"{batch_success} stored, {batch_fail} failed"
                )

        logger.info(f"Fetch complete: {success_count} stored, {failure_count} failed")
        return success_count, failure_count

    def _process_batch(self, session, message_refs):
        """Process batch of messages."""

        success_count = 0
        failure_count = 0
        for msg_ref in message_refs:
            try:
                email = self._fetch_and_transform(msg_ref["id"])
                if email:
                    self._store_email(session, email)
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                logger.error(f"Failed to process message {msg_ref['id']}: {e}")
                failure_count += 1
        try:
            session.commit()
        except Exception as e:
            logger.error(f"Batch commit failed: {e}")
            session.rollback()
            failure_count = len(message_refs)
            success_count = 0

        return success_count, failure_count

    def _fetch_and_transform(self, message_id):
        """Fetch message from Gmail and transform to Email model."""

        message = self.gmail_client.get_message(message_id)
        if not message:
            return None
        try:
            headers = self.gmail_client.extract_headers(message)
            body = self.gmail_client.extract_body(message)
            received_at = self.gmail_client.convert_to_internal_date(
                message.get("internalDate", "0")
            )
            label_ids = message.get("labelIds", [])
            is_read = "UNREAD" not in label_ids

            # Create Email model
            email = Email(
                id=message_id,
                sender=headers["from"],
                subject=headers["subject"],
                message=body,
                received_at=received_at,
                is_read=is_read,
                processed=False,
            )
            return email

        except Exception as e:
            logger.error(f"Failed to transform message {message_id}: {e}")
            return None

    @staticmethod
    def _store_email(session: Session, email: Email) -> None:
        """Store email in database with update or create logic."""

        stmt = (
            insert(Email)
            .values(
                id=email.id,
                sender=email.sender,
                subject=email.subject,
                message=email.message,
                received_at=email.received_at,
                is_read=email.is_read,
                processed=email.processed,
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "sender": email.sender,
                    "subject": email.subject,
                    "message": email.message,
                    "received_at": email.received_at,
                    "is_read": email.is_read,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
        )
        session.execute(stmt)
