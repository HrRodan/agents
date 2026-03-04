"""Tests for the Mail class and payload generation."""

import base64

import pytest

from smtp2go_sendgrid.helpers import (
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
from smtp2go_sendgrid.mail import Mail, _coerce_email


# ── Constructor ──────────────────────────────────────────────────────────────


class TestMailConstructor:
    """Tests for Mail.__init__ with various input types."""

    def test_minimal_plain_text(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="recipient@example.com",
            subject="Test Subject",
            plain_text_content="Hello!",
        )
        payload = mail.get()
        assert payload["sender"] == "sender@example.com"
        assert payload["to"] == ["recipient@example.com"]
        assert payload["subject"] == "Test Subject"
        assert payload["text_body"] == "Hello!"
        assert "html_body" not in payload

    def test_html_content(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="recipient@example.com",
            subject="HTML Test",
            html_content="<h1>Hello</h1>",
        )
        payload = mail.get()
        assert payload["html_body"] == "<h1>Hello</h1>"

    def test_both_plain_and_html(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="recipient@example.com",
            subject="Both",
            plain_text_content="plain",
            html_content="<p>html</p>",
        )
        payload = mail.get()
        assert payload["text_body"] == "plain"
        assert payload["html_body"] == "<p>html</p>"

    def test_from_with_name(self):
        mail = Mail(
            from_email=From("sender@example.com", "Sender Name"),
            to_emails="recipient@example.com",
            subject="Test",
            plain_text_content="body",
        )
        payload = mail.get()
        assert payload["sender"] == "Sender Name <sender@example.com>"

    def test_to_with_name(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails=To("recipient@example.com", "Recipient"),
            subject="Test",
            plain_text_content="body",
        )
        payload = mail.get()
        assert payload["to"] == ["Recipient <recipient@example.com>"]

    def test_from_tuple_inputs(self):
        mail = Mail(
            from_email=("sender@example.com", "Sender"),
            to_emails=("recipient@example.com", "Recipient"),
            subject="Test",
            plain_text_content="body",
        )
        payload = mail.get()
        assert payload["sender"] == "Sender <sender@example.com>"
        assert payload["to"] == ["Recipient <recipient@example.com>"]

    def test_multiple_recipients(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails=[
                "a@example.com",
                "b@example.com",
                To("c@example.com", "C"),
            ],
            subject="Multi",
            plain_text_content="body",
        )
        payload = mail.get()
        assert payload["to"] == [
            "a@example.com",
            "b@example.com",
            "C <c@example.com>",
        ]

    def test_content_objects(self):
        """Content object passthrough in constructor (not just strings)."""
        mail = Mail(
            from_email="sender@example.com",
            to_emails="recipient@example.com",
            subject="Content Object Test",
            plain_text_content=Content(MimeType.text, "plain content"),
        )
        payload = mail.get()
        assert payload["text_body"] == "plain content"

    def test_subject_object(self):
        """Subject helper object works in constructor."""
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject=Subject("Subject Object"),
            plain_text_content="body",
        )
        payload = mail.get()
        assert payload["subject"] == "Subject Object"

    def test_email_object_as_from(self):
        """A generic Email object coerces to From."""
        mail = Mail(
            from_email=Email("sender@example.com", "Sender"),
            to_emails="to@example.com",
            subject="Test",
            plain_text_content="body",
        )
        payload = mail.get()
        assert payload["sender"] == "Sender <sender@example.com>"


# ── Methods ──────────────────────────────────────────────────────────────────


class TestMailMethods:
    """Tests for Mail's add_* methods."""

    def test_add_to(self):
        mail = Mail(from_email="s@e.com", subject="T", plain_text_content="b")
        mail.add_to("a@example.com")
        mail.add_to(To("b@example.com", "B"))
        payload = mail.get()
        assert payload["to"] == ["a@example.com", "B <b@example.com>"]

    def test_add_to_list(self):
        mail = Mail(from_email="s@e.com", subject="T", plain_text_content="b")
        mail.add_to(["a@example.com", "b@example.com"])
        payload = mail.get()
        assert payload["to"] == ["a@example.com", "b@example.com"]

    def test_add_cc(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="CC Test",
            plain_text_content="body",
        )
        mail.add_cc("cc@example.com")
        mail.add_cc(Cc("cc2@example.com", "CC 2"))
        payload = mail.get()
        assert payload["cc"] == ["cc@example.com", "CC 2 <cc2@example.com>"]

    def test_add_bcc(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="BCC Test",
            plain_text_content="body",
        )
        mail.add_bcc("bcc@example.com")
        payload = mail.get()
        assert payload["bcc"] == ["bcc@example.com"]

    def test_add_header(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Header Test",
            plain_text_content="body",
        )
        mail.add_header(Header("X-Custom", "value"))
        payload = mail.get()
        assert payload["custom_headers"] == [{"header": "X-Custom", "value": "value"}]

    def test_add_header_dict(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Test",
            plain_text_content="body",
        )
        mail.add_header({"X-Key": "val"})
        payload = mail.get()
        assert payload["custom_headers"] == [{"header": "X-Key", "value": "val"}]

    def test_add_multiple_headers(self):
        """Multiple add_header calls accumulate."""
        mail = Mail(from_email="s@e.com", to_emails="t@e.com", subject="H")
        mail.add_header(Header("X-A", "1"))
        mail.add_header(Header("X-B", "2"))
        payload = mail.get()
        assert len(payload["custom_headers"]) == 2

    def test_reply_to_with_reply_to_object(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Reply Test",
            plain_text_content="body",
        )
        mail.reply_to = ReplyTo("reply@example.com", "Reply Person")
        payload = mail.get()
        assert {
            "header": "Reply-To",
            "value": "Reply Person <reply@example.com>",
        } in payload["custom_headers"]

    def test_reply_to_with_string(self):
        """Setting reply_to with a plain string should work."""
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Reply Test",
            plain_text_content="body",
        )
        mail.reply_to = "reply@example.com"
        payload = mail.get()
        assert {"header": "Reply-To", "value": "reply@example.com"} in payload[
            "custom_headers"
        ]

    def test_reply_to_with_tuple(self):
        """Setting reply_to with a tuple should work."""
        mail = Mail(
            from_email="s@e.com",
            to_emails="t@e.com",
            subject="T",
            plain_text_content="b",
        )
        mail.reply_to = ("noreply@example.com", "No Reply")
        payload = mail.get()
        assert {
            "header": "Reply-To",
            "value": "No Reply <noreply@example.com>",
        } in payload["custom_headers"]

    def test_attachment(self):
        content_b64 = base64.b64encode(b"file data").decode("ascii")
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Attachment Test",
            plain_text_content="body",
        )
        mail.add_attachment(
            Attachment(
                file_content=content_b64,
                file_name="doc.pdf",
                file_type="application/pdf",
            )
        )
        payload = mail.get()
        assert len(payload["attachments"]) == 1
        assert payload["attachments"][0]["filename"] == "doc.pdf"
        assert payload["attachments"][0]["fileblob"] == content_b64
        assert payload["attachments"][0]["mimetype"] == "application/pdf"

    def test_template_id_and_data(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Template Test",
        )
        mail.template_id = "tmpl-123"
        mail.dynamic_template_data = {"name": "User", "code": "ABC"}
        payload = mail.get()
        assert payload["template_id"] == "tmpl-123"
        assert payload["template_data"] == {"name": "User", "code": "ABC"}

    def test_add_content_method(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="Content Test",
        )
        mail.add_content("plain text", MimeType.text)
        mail.add_content("<p>html</p>", MimeType.html)
        payload = mail.get()
        assert payload["text_body"] == "plain text"
        assert payload["html_body"] == "<p>html</p>"

    def test_add_content_default_mime_type(self):
        """add_content without mime_type defaults to text/plain."""
        mail = Mail(from_email="s@e.com", to_emails="t@e.com", subject="T")
        mail.add_content("just text")
        payload = mail.get()
        assert payload["text_body"] == "just text"

    def test_add_content_with_content_object(self):
        """add_content with a Content object passes through directly."""
        mail = Mail(from_email="s@e.com", to_emails="t@e.com", subject="T")
        mail.add_content(Content(MimeType.html, "<b>bold</b>"))
        payload = mail.get()
        assert payload["html_body"] == "<b>bold</b>"


# ── Method Chaining ──────────────────────────────────────────────────────────


class TestMailChaining:
    """Verify that add_* methods return self for fluent chaining."""

    def test_chaining(self):
        mail = (
            Mail()
            .add_to("to@example.com")
            .add_cc("cc@example.com")
            .add_bcc("bcc@example.com")
            .add_content("body", MimeType.text)
            .add_attachment(Attachment("abc", "f.txt"))
            .add_header(Header("X-A", "1"))
        )
        assert isinstance(mail, Mail)
        payload = mail.get()
        assert payload["to"] == ["to@example.com"]
        assert payload["cc"] == ["cc@example.com"]
        assert payload["bcc"] == ["bcc@example.com"]
        assert payload["text_body"] == "body"
        assert len(payload["attachments"]) == 1
        assert len(payload["custom_headers"]) == 1


# ── Property Setters ─────────────────────────────────────────────────────────


class TestMailPropertySetters:
    """Tests for Mail's property setters."""

    def test_to_setter(self):
        mail = Mail()
        mail.from_email = "sender@example.com"
        mail.to = ["a@example.com", "b@example.com"]
        mail.subject = "Setter Test"
        mail.add_content("body", MimeType.text)
        payload = mail.get()
        assert payload["to"] == ["a@example.com", "b@example.com"]

    def test_to_setter_replaces(self):
        """Setting to= replaces any previously added recipients."""
        mail = Mail(to_emails="old@example.com")
        mail.to = "new@example.com"
        payload = mail.get()
        assert payload["to"] == ["new@example.com"]

    def test_cc_setter(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="CC Setter",
            plain_text_content="body",
        )
        mail.cc = ["cc1@example.com", "cc2@example.com"]
        payload = mail.get()
        assert payload["cc"] == ["cc1@example.com", "cc2@example.com"]

    def test_bcc_setter(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="BCC Setter",
            plain_text_content="body",
        )
        mail.bcc = "bcc@example.com"
        payload = mail.get()
        assert payload["bcc"] == ["bcc@example.com"]

    def test_from_email_setter_string(self):
        mail = Mail()
        mail.from_email = "sender@example.com"
        assert mail.from_email.email == "sender@example.com"

    def test_from_email_setter_tuple(self):
        mail = Mail()
        mail.from_email = ("sender@example.com", "Sender")
        assert mail.from_email.email == "sender@example.com"
        assert mail.from_email.name == "Sender"

    def test_subject_setter_subject_object(self):
        mail = Mail()
        mail.subject = Subject("Custom Subject")
        assert mail.subject.get() == "Custom Subject"


# ── Edge Cases / Payload Shape ───────────────────────────────────────────────


class TestMailEmptyPayload:
    """Test payload omission of empty fields."""

    def test_empty_mail_produces_empty_dict(self):
        mail = Mail()
        payload = mail.get()
        assert payload == {}

    def test_no_content_omits_body_keys(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="No Content",
        )
        payload = mail.get()
        assert "text_body" not in payload
        assert "html_body" not in payload

    def test_no_cc_bcc_omits_keys(self):
        mail = Mail(
            from_email="sender@example.com",
            to_emails="to@example.com",
            subject="No CC/BCC",
            plain_text_content="body",
        )
        payload = mail.get()
        assert "cc" not in payload
        assert "bcc" not in payload
        assert "custom_headers" not in payload
        assert "attachments" not in payload
        assert "template_id" not in payload
        assert "template_data" not in payload


# ── __str__ / __repr__ ───────────────────────────────────────────────────────


class TestMailRepresentation:
    """Test Mail's string representations."""

    def test_str_returns_payload_string(self):
        mail = Mail(
            from_email="s@e.com",
            to_emails="t@e.com",
            subject="Test",
            plain_text_content="body",
        )
        result = str(mail)
        assert "sender" in result
        assert "s@e.com" in result

    def test_repr(self):
        mail = Mail(
            from_email="s@e.com",
            to_emails="t@e.com",
            subject="Test",
        )
        result = repr(mail)
        assert "Mail" in result
        assert "s@e.com" in result


# ── _coerce_email ────────────────────────────────────────────────────────────


class TestCoerceEmail:
    """Tests for the _coerce_email utility function."""

    def test_passthrough_same_class(self):
        t = To("a@b.com")
        assert _coerce_email(t, To) is t

    def test_from_email_base_class(self):
        e = Email("a@b.com", "Name")
        result = _coerce_email(e, To)
        assert isinstance(result, To)
        assert result.email == "a@b.com"
        assert result.name == "Name"

    def test_from_string(self):
        result = _coerce_email("a@b.com", From)
        assert isinstance(result, From)
        assert result.email == "a@b.com"

    def test_from_tuple(self):
        result = _coerce_email(("a@b.com", "Name"), Cc)
        assert isinstance(result, Cc)
        assert result.email == "a@b.com"
        assert result.name == "Name"

    def test_from_tuple_no_name(self):
        result = _coerce_email(("a@b.com",), Bcc)
        assert isinstance(result, Bcc)
        assert result.name is None

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError, match="Cannot coerce"):
            _coerce_email(12345, To)

    def test_invalid_type_raises_with_class_name(self):
        with pytest.raises(TypeError, match="To"):
            _coerce_email(object(), To)


# ── Package-Level Imports ────────────────────────────────────────────────────


class TestPackageImports:
    """Verify all public symbols are importable from the package root."""

    def test_all_symbols_importable(self):
        from smtp2go_sendgrid import (
            Attachment,
            Bcc,
            Cc,
            Content,
            Email,
            From,
            Header,
            Mail,
            MimeType,
            ReplyTo,
            Response,
            SendGridAPIClient,
            Smtp2goAPIClient,
            Subject,
            To,
        )

        # Just confirm they're the correct types
        assert Mail is not None
        assert SendGridAPIClient is Smtp2goAPIClient
