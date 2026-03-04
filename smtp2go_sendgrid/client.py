"""SMTP2GO API client with a SendGrid-compatible interface."""

from __future__ import annotations

import os
from typing import Optional, Union

import requests

from .mail import Mail
from .response import Response

SMTP2GO_API_URL = "https://api.smtp2go.com/v3/email/send"


class Smtp2goAPIClient:
    """Drop-in replacement for ``sendgrid.SendGridAPIClient``.

    Usage is identical to SendGrid::

        client = Smtp2goAPIClient(api_key="your-smtp2go-key")
        # or rely on SMTP2GO_API_KEY env var
        client = Smtp2goAPIClient()

        mail = Mail(from_email, to_emails, subject, content)
        response = client.send(mail)
        print(response.status_code)
        print(response.body)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = SMTP2GO_API_URL,
    ) -> None:
        self.api_key = api_key or os.environ.get("SMTP2GO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "An SMTP2GO API key is required. Pass it directly or set "
                "the SMTP2GO_API_KEY environment variable."
            )
        self.host = host
        self.client = _FluentClient(self)

    def send(self, message: Union[Mail, dict]) -> Response:
        """Send an email via the SMTP2GO v3 API.

        :param message: A ``Mail`` object or a raw dict payload.
        :returns: A ``Response`` with ``status_code``, ``body``, and ``headers``.
        """
        if isinstance(message, dict):
            payload = message
        else:
            payload = message.get()

        payload["api_key"] = self.api_key

        http_response = requests.post(
            self.host,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30,
        )

        return Response(
            status_code=http_response.status_code,
            body=http_response.text,
            headers=dict(http_response.headers),
        )

    def __repr__(self) -> str:
        masked = f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key else "None"
        return f"Smtp2goAPIClient(api_key={masked!r})"


# ── Fluent API Support ────────────────────────────────────────────────────────


class _FluentSend:
    """Supports .send syntax."""

    def __init__(self, api_client: Smtp2goAPIClient) -> None:
        self._api_client = api_client

    def post(self, request_body: Union[Mail, dict] = None, **_kwargs) -> Response:
        """Support for fluent SendGrid syntax: .post(request_body=mail)"""
        if request_body is None:
            raise ValueError("request_body is required for fluent .post()")
        return self._api_client.send(request_body)


class _FluentMail:
    """Supports .mail syntax."""

    def __init__(self, api_client: Smtp2goAPIClient) -> None:
        self.send = _FluentSend(api_client)


class _FluentClient:
    """Supports .client syntax."""

    def __init__(self, api_client: Smtp2goAPIClient) -> None:
        self.mail = _FluentMail(api_client)


# Alias for true drop-in replacement of SendGrid imports.
SendGridAPIClient = Smtp2goAPIClient
