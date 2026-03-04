"""Mail class mirroring SendGrid's Mail helper, producing SMTP2GO-compatible payloads."""

from __future__ import annotations

from typing import Optional, Union

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


class Mail:
    """Build an email message using the same interface as SendGrid's Mail helper.

    Typical usage (identical to SendGrid)::

        mail = Mail(
            from_email="sender@example.com",
            to_emails="recipient@example.com",
            subject="Hello",
            plain_text_content="world",
        )

    Calling ``mail.get()`` returns a dict formatted for the SMTP2GO
    ``/v3/email/send`` endpoint.
    """

    def __init__(
        self,
        from_email: Optional[Union[From, Email, str, tuple]] = None,
        to_emails: Optional[Union[To, Email, str, tuple, list]] = None,
        subject: Optional[Union[Subject, str]] = None,
        plain_text_content: Optional[Union[Content, str]] = None,
        html_content: Optional[Union[Content, str]] = None,
        is_multiple: bool = False,
    ) -> None:
        """Build an email message.

        All parameters accept the same flexible types as SendGrid.

        :param from_email:          Sender — ``From``, ``Email``, ``str``, or
                                    ``(email, name)`` tuple.
        :param to_emails:           Recipient(s) — ``To``, ``str``, ``tuple``,
                                    or a list of any of those.
        :param subject:             Subject line — ``Subject`` or ``str``.
        :param plain_text_content:  Plain-text body — ``Content`` or ``str``.
        :param html_content:        HTML body — ``Content`` or ``str``.
        :param is_multiple:         Unused — kept for SendGrid signature compat.
        """
        self._from_email: Optional[From] = None
        self._subject: Optional[Subject] = None
        self._to: list[To] = []
        self._cc: list[Cc] = []
        self._bcc: list[Bcc] = []
        self._contents: list[Content] = []
        self._attachments: list[Attachment] = []
        self._headers: list[Header] = []
        self._reply_to: Optional[ReplyTo] = None
        self._template_id: Optional[str] = None
        self._template_data: Optional[dict] = None

        if from_email is not None:
            self.from_email = from_email
        if to_emails is not None:
            self._add_emails(to_emails, self._to, To, is_multiple)
        if subject is not None:
            self.subject = subject
        if plain_text_content is not None:
            self.add_content(plain_text_content, MimeType.text)
        if html_content is not None:
            self.add_content(html_content, MimeType.html)

    # ── from_email ──────────────────────────────────────────────────────

    @property
    def from_email(self) -> Optional[From]:
        """The sender email address."""
        return self._from_email

    @from_email.setter
    def from_email(self, value: Union[From, Email, str, tuple]) -> None:
        self._from_email = _coerce_email(value, From)

    # ── subject ─────────────────────────────────────────────────────────

    @property
    def subject(self) -> Optional[Subject]:
        """The email subject."""
        return self._subject

    @subject.setter
    def subject(self, value: Union[Subject, str]) -> None:
        if isinstance(value, Subject):
            self._subject = value
        else:
            self._subject = Subject(value)

    # ── to / cc / bcc ───────────────────────────────────────────────────

    def add_to(
        self,
        email: Union[To, Email, str, tuple, list],
        **_kwargs,
    ) -> "Mail":
        """Add one or more To recipients.

        :param email: Recipient address(es) — accepts the same flexible types
                      as the constructor's ``to_emails``.
        :returns: ``self`` for chaining.
        """
        self._add_emails(email, self._to, To)
        return self

    def add_cc(
        self,
        email: Union[Cc, Email, str, tuple, list],
        **_kwargs,
    ) -> "Mail":
        """Add one or more CC recipients.

        :param email: CC address(es).
        :returns: ``self`` for chaining.
        """
        self._add_emails(email, self._cc, Cc)
        return self

    def add_bcc(
        self,
        email: Union[Bcc, Email, str, tuple, list],
        **_kwargs,
    ) -> "Mail":
        """Add one or more BCC recipients.

        :param email: BCC address(es).
        :returns: ``self`` for chaining.
        """
        self._add_emails(email, self._bcc, Bcc)
        return self

    @property
    def to(self) -> list[To]:
        """The current list of To recipients."""
        return self._to

    @to.setter
    def to(self, value: Union[To, Email, str, tuple, list]) -> None:
        self._to = []
        self._add_emails(value, self._to, To)

    @property
    def cc(self) -> list[Cc]:
        """The current list of CC recipients."""
        return self._cc

    @cc.setter
    def cc(self, value: Union[Cc, Email, str, tuple, list]) -> None:
        self._cc = []
        self._add_emails(value, self._cc, Cc)

    @property
    def bcc(self) -> list[Bcc]:
        """The current list of BCC recipients."""
        return self._bcc

    @bcc.setter
    def bcc(self, value: Union[Bcc, Email, str, tuple, list]) -> None:
        self._bcc = []
        self._add_emails(value, self._bcc, Bcc)

    # ── content ─────────────────────────────────────────────────────────

    @property
    def contents(self) -> list[Content]:
        """The current list of content blocks."""
        return self._contents

    def add_content(
        self,
        content: Union[Content, str],
        mime_type: Optional[Union[MimeType, str]] = None,
    ) -> "Mail":
        """Add a content block to the email.

        :param content:   A ``Content`` object, or a plain string body.
        :param mime_type: MIME type — required when *content* is a ``str``;
                          defaults to ``MimeType.text`` if omitted.
        :returns: ``self`` for chaining.
        """
        if isinstance(content, str):
            if mime_type is None:
                mime_type = MimeType.text
            content = Content(mime_type, content)
        self._contents.append(content)
        return self

    # ── attachments ─────────────────────────────────────────────────────

    @property
    def attachments(self) -> list[Attachment]:
        """The current list of attachments."""
        return self._attachments

    def add_attachment(self, attachment: Attachment) -> "Mail":
        """Add a file attachment.

        :param attachment: An :class:`Attachment` instance.
        :returns: ``self`` for chaining.
        """
        self._attachments.append(attachment)
        return self

    # ── headers ──────────────────────────────────────────────────────────

    @property
    def headers(self) -> list[Header]:
        """The current list of custom headers."""
        return self._headers

    def add_header(self, header: Union[Header, dict]) -> "Mail":
        """Add a custom header.

        :param header: A ``Header`` object or a ``{key: value}`` dict.
        :returns: ``self`` for chaining.
        """
        if isinstance(header, dict):
            for k, v in header.items():
                self._headers.append(Header(k, v))
        else:
            self._headers.append(header)
        return self

    # ── reply_to ─────────────────────────────────────────────────────────

    @property
    def reply_to(self) -> Optional[ReplyTo]:
        """The Reply-To address."""
        return self._reply_to

    @reply_to.setter
    def reply_to(self, value: Union[ReplyTo, Email, str, tuple]) -> None:
        self._reply_to = _coerce_email(value, ReplyTo)

    # ── template ─────────────────────────────────────────────────────────

    @property
    def template_id(self) -> Optional[str]:
        """The SMTP2GO template ID."""
        return self._template_id

    @template_id.setter
    def template_id(self, value: str) -> None:
        self._template_id = value

    @property
    def dynamic_template_data(self) -> Optional[dict]:
        """Template variable data (passed as ``template_data`` to SMTP2GO)."""
        return self._template_data

    @dynamic_template_data.setter
    def dynamic_template_data(self, value: dict) -> None:
        self._template_data = value

    # ── payload builder ──────────────────────────────────────────────────

    def get(self) -> dict:
        """Build the SMTP2GO ``/v3/email/send`` request body.

        Returns a dict ready to be JSON-serialised and POSTed.
        """
        payload: dict = {}

        # sender
        if self._from_email:
            payload["sender"] = self._from_email.formatted

        # recipients
        if self._to:
            payload["to"] = [e.formatted for e in self._to]
        if self._cc:
            payload["cc"] = [e.formatted for e in self._cc]
        if self._bcc:
            payload["bcc"] = [e.formatted for e in self._bcc]

        # subject
        if self._subject:
            payload["subject"] = self._subject.get()

        # body content
        for content in self._contents:
            if content.mime_type == MimeType.text.value:
                payload["text_body"] = content.value
            elif content.mime_type == MimeType.html.value:
                payload["html_body"] = content.value

        # attachments
        if self._attachments:
            payload["attachments"] = [a.get() for a in self._attachments]

        # custom headers (including Reply-To)
        custom_headers: list[dict] = []
        if self._reply_to:
            custom_headers.append(
                {"header": "Reply-To", "value": self._reply_to.formatted}
            )
        for h in self._headers:
            custom_headers.append(h.get())
        if custom_headers:
            payload["custom_headers"] = custom_headers

        # templates
        if self._template_id:
            payload["template_id"] = self._template_id
        if self._template_data:
            payload["template_data"] = self._template_data

        return payload

    def __str__(self) -> str:
        return str(self.get())

    def __repr__(self) -> str:
        return (
            f"Mail(from_email={self._from_email!r}, "
            f"to={self._to!r}, subject={self._subject!r})"
        )

    # ── private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _add_emails(
        emails: Union[Email, str, tuple, list],
        target: list,
        cls: type,
        _is_multiple: bool = False,
    ) -> None:
        if isinstance(emails, list):
            for item in emails:
                target.append(_coerce_email(item, cls))
        else:
            target.append(_coerce_email(emails, cls))


def _coerce_email(value, cls: type):
    """Normalise various input forms into the target Email subclass.

    :param value: An ``Email`` subclass instance, ``str``, or ``(email, name)``
                  tuple.
    :param cls:   The target Email subclass (e.g. ``To``, ``From``).
    :returns:     An instance of *cls*.
    :raises TypeError: If *value* cannot be coerced.
    """
    if isinstance(value, cls):
        return value
    if isinstance(value, Email):
        return cls(value.email, value.name)
    if isinstance(value, str):
        return cls(value)
    if isinstance(value, tuple):
        return cls(value[0], value[1] if len(value) > 1 else None)
    raise TypeError(f"Cannot coerce {type(value)} to {cls.__name__}")
