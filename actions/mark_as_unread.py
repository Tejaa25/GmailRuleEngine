from actions import register_action
from database import Email
from services import GmailClient
from utils import get_logger

logger = get_logger(__name__)


@register_action("mark_as_unread")
def execute(gmail_client: GmailClient, email: Email, params: dict) -> bool:
    """Mark an email as unread."""

    try:
        success = gmail_client.modify_message(
            message_id=email.id, add_labels=["UNREAD"]
        )
        if success:
            email.is_read = False
            logger.info(f"Marked email {email.id} as unread.")
            return True
        else:
            logger.warning(f"Failed to mark email {email.id} as unread.")
            return False
    except Exception as e:
        logger.error(f"Error marking email {email.id} as unread: {e}")
        return False
