import pickle
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import Config


class GmailAuthenticator:
    """
    Handles Gmail API authentication and credential management.
    This class have all the authentication logic.
    """
    
    def __init__(
        self,
        credentials_path: Path = Config.CREDENTIALS_PATH,
        token_path: Path = Config.TOKEN_PATH,
        scopes: list[str] = Config.GMAIL_SCOPES
    ):
        """Initialize the authenticator."""

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes
        self._credentials = None
    
    def authenticate(self) -> Credentials:
        """Authenticate and return valid credentials."""

        self._credentials = self._run_oauth_flow()
        self._save_token()
        return self._credentials

    def _save_token(self) -> None:
        """Save credentials to token file."""

        try:
            with self.token_path.open("wb") as token_file:
                pickle.dump(self._credentials, token_file)
        except Exception as e:
            raise
    
    def _run_oauth_flow(self) -> Credentials:
        """Run the OAuth authorization flow."""

        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. ")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path),
                self.scopes
            )
            credentials = flow.run_local_server(port=0)
            return credentials
        except Exception as e:
            raise