import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central config class for this app."""

    BASE_DIR = Path(__file__).parent
    TOKEN_PATH = BASE_DIR / "token.pkl"
    CREDENTIALS_PATH = BASE_DIR / "credentials.json"
    RULES_FILE = BASE_DIR / "rules.json"
    
    # Gmail API
    GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    GMAIL_API_VERSION = "v1"
    
    # DB config
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_PORT = os.getenv("DATABASE_PORT")
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    @classmethod
    def get_db_url(cls) -> str:
        """Returns database URL."""
        return (
            f"postgresql://{cls.DATABASE_USER}:{cls.DATABASE_PASSWORD}"
            f"@{cls.DATABASE_HOST}:{cls.DATABASE_PORT}/{cls.DATABASE_NAME}"
        )
