from actions import register_action
from database import Email
from services import GmailClient
from utils.logger import get_logger

logger = get_logger(__name__)


@register_action("mark_as_read")
def execute(gmail_client: GmailClient, email: Email, params: dict) -> bool:
    """Mark an email as read."""

    try:
        success = gmail_client.modify_message(
            message_id=email.id, remove_labels=["UNREAD"]
        )
        if success:
            email.is_read = True # Update database
            logger.info(f"Marked email {email.id} as read.")
            return True
        else:
            logger.warning(f"Failed to mark email {email.id} as read.")
            return False
    except Exception as e:
        logger.error(f"Error marking email {email.id} as read: {e}")
        return False
