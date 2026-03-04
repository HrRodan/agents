"""Lightweight helper classes mirroring the SendGrid Python SDK type system."""

from __future__ import annotations

import base64
from enum import Enum
from pathlib import Path
from typing import Optional


class MimeType(Enum):
    """MIME types for email content."""

    text = "text/plain"
    html = "text/html"


class Email:
    """Base email address container.

    Accepts the same input styles as SendGrid's Email helper:
        Email("user@example.com")
        Email("user@example.com", "Display Name")
        Email(("user@example.com", "Display Name"))
    """

    def __init__(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialise an email address.

        :param email: Email address string, or a ``(email, name)`` tuple.
        :param name:  Optional display name.
        """
        if isinstance(email, tuple):
            email, name = email[0], email[1] if len(email) > 1 else None
        self.email: Optional[str] = email
        self.name: Optional[str] = name

    def get(self) -> dict:
        """Return a dict representation ``{"email": ..., "name": ...}``."""
        result: dict = {"email": self.email}
        if self.name:
            result["name"] = self.name
        return result

    @property
    def formatted(self) -> str:
        """Return RFC 5322 formatted address."""
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email or ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(email={self.email!r}, name={self.name!r})"


class From(Email):
    """Sender email address."""


class To(Email):
    """Recipient email address."""


class Cc(Email):
    """CC email address."""


class Bcc(Email):
    """BCC email address."""


class ReplyTo(Email):
    """Reply-To email address."""


class Subject:
    """Email subject wrapper."""

    def __init__(self, subject: str) -> None:
        """Initialise a Subject.

        :param subject: The subject line text.
        """
        self.subject = subject

    def get(self) -> str:
        """Return the subject string."""
        return self.subject

    def __repr__(self) -> str:
        return f"Subject({self.subject!r})"


class Content:
    """Email content container.

    Usage mirrors SendGrid:
        Content("text/plain", "Hello world")
        Content(MimeType.html, "<h1>Hello</h1>")
    """

    def __init__(self, mime_type: str | MimeType, value: str) -> None:
        """Initialise a Content block.

        :param mime_type: MIME type string (e.g. ``"text/plain"``) or a
                          :class:`MimeType` enum member.
        :param value:     The content body.
        """
        if isinstance(mime_type, MimeType):
            self.mime_type = mime_type.value
        else:
            self.mime_type = mime_type
        self.value = value

    def get(self) -> dict:
        """Return ``{"type": <mime_type>, "value": <body>}``."""
        return {"type": self.mime_type, "value": self.value}

    def __repr__(self) -> str:
        return f"Content(mime_type={self.mime_type!r}, value={self.value[:40]!r}...)"


class Header:
    """Custom email header."""

    def __init__(self, key: str, value: str) -> None:
        """Initialise a custom email header.

        :param key:   Header name (e.g. ``"X-Custom-Id"``).
        :param value: Header value.
        """
        self.key = key
        self.value = value

    def get(self) -> dict:
        """Return SMTP2GO header format ``{"header": ..., "value": ...}``."""
        return {"header": self.key, "value": self.value}

    def __repr__(self) -> str:
        return f"Header({self.key!r}, {self.value!r})"


class Attachment:
    """Email attachment.

    Mirrors SendGrid's Attachment helper. ``file_content`` must be a
    base64-encoded string (same as SendGrid).

    Convenience: use ``Attachment.from_file(path)`` to read and encode a local
    file automatically.
    """

    def __init__(
        self,
        file_content: str,
        file_name: str,
        file_type: Optional[str] = None,
        disposition: Optional[str] = None,
        content_id: Optional[str] = None,
    ) -> None:
        """Initialise an attachment.

        :param file_content: Base64-encoded file content (same as SendGrid).
        :param file_name:    Filename shown to the recipient.
        :param file_type:    MIME type (default ``application/octet-stream``).
        :param disposition:  Content disposition (SendGrid compat, not sent to
                             SMTP2GO).
        :param content_id:   Content-ID for inline attachments (SendGrid compat,
                             not sent to SMTP2GO).
        """
        self.file_content = file_content
        self.file_name = file_name
        self.file_type = file_type or "application/octet-stream"
        self.disposition = disposition
        self.content_id = content_id

    def get(self) -> dict:
        """Return SMTP2GO attachment format ``{filename, fileblob, mimetype}``."""
        return {
            "filename": self.file_name,
            "fileblob": self.file_content,
            "mimetype": self.file_type,
        }

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        file_type: Optional[str] = None,
    ) -> "Attachment":
        """Create an Attachment by reading and base64-encoding a local file."""
        p = Path(path)
        raw = p.read_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        return cls(
            file_content=encoded,
            file_name=p.name,
            file_type=file_type,
        )

    def __repr__(self) -> str:
        return f"Attachment(file_name={self.file_name!r}, file_type={self.file_type!r})"
