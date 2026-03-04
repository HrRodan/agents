"""Response wrapper matching the SendGrid response interface."""

from __future__ import annotations

from typing import Optional


class Response:
    """Thin wrapper around the HTTP response from SMTP2GO.

    Provides the same attribute interface as SendGrid's response object:
    ``status_code``, ``body``, and ``headers``.
    """

    def __init__(
        self,
        status_code: int,
        body: str,
        headers: Optional[dict] = None,
    ) -> None:
        """Wrap an HTTP response.

        :param status_code: HTTP status code (e.g. ``200``).
        :param body:        Response body as a string.
        :param headers:     Response headers as a dict.
        """
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}

    def __repr__(self) -> str:
        return f"Response(status_code={self.status_code})"
