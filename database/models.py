from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Email(Base):
    """
    Model to store emails fetched from Gmail.
    The Gmail message ID is used as primary key for idempotency.
    """

    __tablename__ = "emails"

    id = Column(String(255), primary_key=True, comment="Gmail message ID (unique identifier)")
    sender = Column(String(500), nullable=False, index=True)
    subject = Column(String(1000), nullable=False)
    message = Column(Text, nullable=True)
    received_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )
    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    processed = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    __table_args__ = (Index("idx_unprocessed_emails", "processed", "is_read"),)

    def __repr__(self) -> str:
        """String representation for debugging."""

        return (
            f"<Email(id='{self.id[:10]}...', "
            f"sender='{self.sender}', "
            f"subject='{self.subject[:30]}...', "
            f"received_at='{self.received_at}')>"
        )
