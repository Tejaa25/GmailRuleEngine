from actions import register_action
from database import Email
from services import GmailClient
from utils import get_logger

logger = get_logger(__name__)


@register_action("move_message")
def execute(gmail_client: GmailClient, email: Email, params: dict) -> bool:
    """Move email to the given destination."""

    destination = params.get("destination")
    if not destination:
        logger.error("'destination' required for move_message action.")
        return False
    try:
        label_id = gmail_client.get_label_id(destination)
        if not label_id:
            logger.warning(f"Label '{destination}' not found for email {email.id}.")
            return False
        success = gmail_client.modify_message(
            message_id=email.id, add_labels=[label_id]
        )
        if success:
            logger.info(f"Moved email {email.id} to '{destination}'")
            return True
        else:
            logger.warning(f"Failed to move email {email.id} to '{destination}'")
            return False
    except Exception as e:
        logger.error(f"Error moving email {email.id}: {e}")
        return False
