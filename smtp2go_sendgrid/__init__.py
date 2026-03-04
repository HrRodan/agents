"""smtp2go_sendgrid — Drop-in replacement for the SendGrid Python SDK using the SMTP2GO API.

Usage (mirrors SendGrid exactly)::

    from smtp2go_sendgrid import Smtp2goAPIClient, Mail, From, To, Content

    client = Smtp2goAPIClient(api_key="your-smtp2go-api-key")
    mail = Mail(
        from_email=From("sender@example.com", "Sender"),
        to_emails=To("recipient@example.com"),
        subject="Hello",
        plain_text_content="world",
    )
    response = client.send(mail)
    print(response.status_code, response.body)
"""

from .client import SendGridAPIClient, Smtp2goAPIClient
from .helpers import (
    Attachment,
    Bcc,
    Cc,
    Content,
    Email,
    From,
    Header,
    MimeType,
    ReplyTo,
    Subject,
    To,
)
from .mail import Mail
from .response import Response

__all__ = [
    "Smtp2goAPIClient",
    "SendGridAPIClient",
    "Mail",
    "Email",
    "From",
    "To",
    "Cc",
    "Bcc",
    "Content",
    "MimeType",
    "Header",
    "Attachment",
    "ReplyTo",
    "Subject",
    "Response",
]
