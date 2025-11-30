from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class GmailClient:
    """This class is for fetching and modifying emails."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = self._build_service()
        self._label_cache = None

    def _build_service(self):

        try:
            service = build(
                "gmail",
                Config.GMAIL_API_VERSION,
                credentials=self.credentials,
                cache_discovery=False,
            )
            logger.info("Gmail service initialized")
            return service
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            raise
