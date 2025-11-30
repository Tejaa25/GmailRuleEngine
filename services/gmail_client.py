import base64
import time
from typing import Dict, Any
from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class GmailClient:
    """This class is for fetching and modifying emails."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = self._build_service()

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

    def list_messages(self):
        """Returns the List of message with 'id' and 'threadId'"""

        messages = []
        max_results = Config.MAX_RESULTS_PER_QUERY
        try:
            request = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=min(max_results, 500),
                )
            )
            while request is not None and len(messages) < max_results:
                response = self._execute_with_retry(request)
                batch = response.get("messages", [])
                messages.extend(batch)
                if len(messages) >= max_results:
                    messages = messages[:max_results]
                    break
                request = self.service.users().messages().list_next(request, response)

            logger.info(f"Listed {len(messages)} messages")
            return messages
        except HttpError as e:
            logger.error(f"Failed to list messages: {e}")
            return []

    def get_message(self, message_id: str):
        """Get the full message."""

        try:
            message = self._execute_with_retry(
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
            )
            return message
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Message {message_id} not found")
            else:
                logger.error(f"Failed to get message {message_id}: {e}")
            return None

    def modify_message(self, message_id, add_labels=None, remove_labels=None) -> bool:

        try:
            body = {}
            if add_labels:
                body["addLabelIds"] = add_labels
            if remove_labels:
                body["removeLabelIds"] = remove_labels
            if not body:
                logger.warning(f"No modifications specified for {message_id}")
                return False
            self._execute_with_retry(
                self.service.users()
                .messages()
                .modify(userId="me", id=message_id, body=body)
            )
            logger.debug(f"Modified message {message_id}")
            return True
        except HttpError as e:
            logger.error(f"Failed to modify message {message_id}: {e}")
            return False

    def get_labels(self):
        try:
            response = self._execute_with_retry(
                self.service.users().labels().list(userId="me")
            )
            return response.get("labels", [])
        except HttpError as e:
            logger.error(f"Failed to get labels: {e}")
            return {}

    def get_label_id(self, label_name: str):

        return self.get_labels().get(label_name.upper())

    @staticmethod
    def extract_headers(message):
        """Extract headers from message."""

        headers = message.get("payload", {}).get("headers", [])
        header_dict = {h["name"].lower(): h["value"] for h in headers}
        return {
            "from": header_dict.get("from", ""),
            "to": header_dict.get("to", ""),
            "subject": header_dict.get("subject", ""),
            "date": header_dict.get("date", ""),
        }

    @staticmethod
    def extract_body(message: Dict[str, Any]) -> str:
        """Extract body from message."""

        payload = message.get("payload", {})

        # Try direct body data
        if "data" in payload.get("body", {}):
            return GmailClient._decode_body(payload["body"]["data"])

        # Try parts (multipart message)
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                body_data = part.get("body", {}).get("data")
                if body_data:
                    return GmailClient._decode_body(body_data)
        return ""

    @staticmethod
    def _decode_body(data: str) -> str:
        """Decode base64 URL-safe body data."""

        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Failed to decode body: {e}")
            return ""

    @staticmethod
    def convert_to_internal_date(internal_date_ms: str) -> datetime:

        try:
            timestamp_sec = int(internal_date_ms) / 1000
            return datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to convert date {internal_date_ms}: {e}")
            return datetime.now(timezone.utc)

    def _execute_with_retry(self, request):
        """Execute API request with exponential backoff retry and return the api response."""

        max_retries = 3
        base_delay = 1
        for attempt in range(max_retries):
            try:
                return request.execute()
            except HttpError as e:
                if e.resp.status in [429, 500, 503] and attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    logger.warning(f"API error {e.resp.status}. Retrying...")
                    time.sleep(delay)
                else:
                    raise
        raise HttpError(resp={"status": 500}, content=b"Max retries exceeded")
