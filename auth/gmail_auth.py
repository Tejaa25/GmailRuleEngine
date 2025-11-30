import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class GmailAuthenticator:
    """
    Handles Gmail API authentication and credential management.
    This class have all the authentication logic.
    """

    def __init__(
        self,
        credentials_path: Path = Config.CREDENTIALS_PATH,
        token_path: Path = Config.TOKEN_PATH,
        scopes: list[str] = Config.GMAIL_SCOPES,
    ):
        """Initialize the authenticator."""

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes
        self._credentials = None

    def authenticate(self) -> Credentials:
        """Authenticate and return valid credentials."""

        if self._credentials and self._credentials.valid:
            return self._credentials
        self._credentials = self._load_token()  # try loading the existing token
        if self._credentials:
            if self._credentials.valid:
                logger.info("Using existing valid credentials")
                return self._credentials
            if self._credentials.expired and self._credentials.refresh_token:
                try:
                    logger.info("Refreshing expired credentials")
                    self._credentials.refresh(Request())
                    self._save_token()
                    logger.info("Credentials refreshed successfully")
                    return self._credentials
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}. Re-authenticating.")
                    self._credentials = None
        if not self._credentials:  # Run OAuth flow if needed
            self._credentials = self._run_oauth_flow()
            self._save_token()
        return self._credentials

    def _load_token(self):
        """Load credentials from token file."""

        if not self.token_path.exists():
            logger.info("No existing token found")
            return None
        try:
            with self.token_path.open("rb") as token_file:
                credentials = pickle.load(token_file)
                logger.info("Token loaded successfully")
                return credentials
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None

    def _save_token(self) -> None:
        """Save credentials to token file."""

        try:
            with self.token_path.open("wb") as token_file:
                pickle.dump(self._credentials, token_file)
                logger.info(f"Token saved to {self.token_path}")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
            raise

    def _run_oauth_flow(self) -> Credentials:
        """Run the OAuth authorization flow."""

        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Credentials file not found at {self.credentials_path}. "
            )
        try:
            logger.info("Starting OAuth flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), self.scopes
            )
            credentials = flow.run_local_server(port=0)
            logger.info("OAuth flow completed.")
            return credentials
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            raise

    def invalidate_token(self) -> None:
        """Function to remove stored token, and re-authenticate next time."""

        if self.token_path.exists():
            self.token_path.unlink()
            logger.info("Token invalidated")
        self._credentials = None
