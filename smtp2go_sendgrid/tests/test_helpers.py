"""Tests for the helper classes."""

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


# ── Email ────────────────────────────────────────────────────────────────────


class TestEmail:
    """Tests for the base Email container."""

    def test_from_string(self):
        e = Email("user@example.com")
        assert e.email == "user@example.com"
        assert e.name is None

    def test_from_string_with_name(self):
        e = Email("user@example.com", "User")
        assert e.email == "user@example.com"
        assert e.name == "User"

    def test_from_tuple(self):
        e = Email(("user@example.com", "User"))
        assert e.email == "user@example.com"
        assert e.name == "User"

    def test_from_tuple_email_only(self):
        """A single-element tuple should set name to None."""
        e = Email(("user@example.com",))
        assert e.email == "user@example.com"
        assert e.name is None

    def test_formatted_with_name(self):
        e = Email("user@example.com", "User")
        assert e.formatted == "User <user@example.com>"

    def test_formatted_without_name(self):
        e = Email("user@example.com")
        assert e.formatted == "user@example.com"

    def test_formatted_none_email(self):
        """If email is None, formatted returns empty string."""
        e = Email()
        assert e.formatted == ""

    def test_get_without_name(self):
        e = Email("user@example.com")
        assert e.get() == {"email": "user@example.com"}

    def test_get_with_name(self):
        e = Email("user@example.com", "User")
        assert e.get() == {"email": "user@example.com", "name": "User"}

    def test_repr(self):
        e = Email("user@example.com", "User")
        assert "Email" in repr(e)
        assert "user@example.com" in repr(e)
        assert "User" in repr(e)


# ── Email Subclasses ─────────────────────────────────────────────────────────


class TestEmailSubclasses:
    """Verify all Email subclasses inherit behaviour correctly."""

    def test_from_is_email(self):
        f = From("sender@example.com", "Sender")
        assert isinstance(f, Email)
        assert f.formatted == "Sender <sender@example.com>"

    def test_to_is_email(self):
        t = To("to@example.com")
        assert isinstance(t, Email)

    def test_cc_is_email(self):
        c = Cc("cc@example.com")
        assert isinstance(c, Email)

    def test_bcc_is_email(self):
        b = Bcc("bcc@example.com")
        assert isinstance(b, Email)

    def test_reply_to_is_email(self):
        r = ReplyTo("reply@example.com", "Reply")
        assert isinstance(r, Email)
        assert r.formatted == "Reply <reply@example.com>"

    def test_subclass_repr_shows_class_name(self):
        """__repr__ should show the subclass name, not 'Email'."""
        assert "From" in repr(From("a@b.com"))
        assert "To" in repr(To("a@b.com"))
        assert "Cc" in repr(Cc("a@b.com"))
        assert "Bcc" in repr(Bcc("a@b.com"))
        assert "ReplyTo" in repr(ReplyTo("a@b.com"))


# ── Subject ──────────────────────────────────────────────────────────────────


class TestSubject:
    """Tests for the Subject wrapper."""

    def test_get(self):
        s = Subject("Hello World")
        assert s.get() == "Hello World"

    def test_repr(self):
        s = Subject("Hello")
        assert "Hello" in repr(s)


# ── Content ──────────────────────────────────────────────────────────────────


class TestContent:
    """Tests for the Content container."""

    def test_plain_text(self):
        c = Content("text/plain", "Hello")
        assert c.get() == {"type": "text/plain", "value": "Hello"}

    def test_html(self):
        c = Content(MimeType.html, "<h1>Hi</h1>")
        assert c.get() == {"type": "text/html", "value": "<h1>Hi</h1>"}

    def test_mime_type_enum(self):
        c = Content(MimeType.text, "Hello")
        assert c.mime_type == "text/plain"

    def test_repr(self):
        c = Content("text/plain", "Hello")
        assert "text/plain" in repr(c)


# ── Header ───────────────────────────────────────────────────────────────────


class TestHeader:
    """Tests for the Header wrapper."""

    def test_get(self):
        h = Header("X-Custom", "value123")
        assert h.get() == {"header": "X-Custom", "value": "value123"}

    def test_repr(self):
        h = Header("X-Foo", "bar")
        assert "X-Foo" in repr(h)
        assert "bar" in repr(h)


# ── Attachment ───────────────────────────────────────────────────────────────


class TestAttachment:
    """Tests for the Attachment helper."""

    def test_get(self):
        content = base64.b64encode(b"hello").decode("ascii")
        a = Attachment(
            file_content=content,
            file_name="test.txt",
            file_type="text/plain",
        )
        result = a.get()
        assert result["filename"] == "test.txt"
        assert result["fileblob"] == content
        assert result["mimetype"] == "text/plain"

    def test_default_file_type(self):
        """When file_type is omitted it defaults to application/octet-stream."""
        a = Attachment(file_content="abc", file_name="blob.bin")
        assert a.file_type == "application/octet-stream"
        assert a.get()["mimetype"] == "application/octet-stream"

    def test_from_file(self, tmp_path):
        test_file = tmp_path / "sample.txt"
        test_file.write_text("hello world")
        a = Attachment.from_file(test_file, file_type="text/plain")
        assert a.file_name == "sample.txt"
        assert a.file_type == "text/plain"
        decoded = base64.b64decode(a.file_content)
        assert decoded == b"hello world"

    def test_from_file_default_type(self, tmp_path):
        """from_file without explicit type defaults to octet-stream."""
        test_file = tmp_path / "data.bin"
        test_file.write_bytes(b"\x00\x01\x02")
        a = Attachment.from_file(test_file)
        assert a.file_type == "application/octet-stream"

    def test_repr(self):
        a = Attachment(
            file_content="abc", file_name="doc.pdf", file_type="application/pdf"
        )
        assert "doc.pdf" in repr(a)
        assert "application/pdf" in repr(a)


# ── MimeType ─────────────────────────────────────────────────────────────────


class TestMimeType:
    """Tests for the MimeType enum."""

    def test_values(self):
        assert MimeType.text.value == "text/plain"
        assert MimeType.html.value == "text/html"

    def test_enum_members(self):
        assert hasattr(MimeType, "text")
        assert hasattr(MimeType, "html")
