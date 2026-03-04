"""Tests for the Smtp2goAPIClient."""

from unittest.mock import MagicMock, patch

import pytest

from smtp2go_sendgrid.client import SendGridAPIClient, Smtp2goAPIClient
from smtp2go_sendgrid.mail import Mail
from smtp2go_sendgrid.response import Response


# ── Init ─────────────────────────────────────────────────────────────────────


class TestSmtp2goAPIClientInit:
    """Tests for client initialisation and API key handling."""

    def test_api_key_from_argument(self):
        client = Smtp2goAPIClient(api_key="test-key-123")
        assert client.api_key == "test-key-123"

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("SMTP2GO_API_KEY", "env-key-456")
        client = Smtp2goAPIClient()
        assert client.api_key == "env-key-456"

    def test_api_key_argument_takes_precedence(self, monkeypatch):
        monkeypatch.setenv("SMTP2GO_API_KEY", "env-key")
        client = Smtp2goAPIClient(api_key="arg-key")
        assert client.api_key == "arg-key"

    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("SMTP2GO_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required"):
            Smtp2goAPIClient()

    def test_custom_host(self):
        client = Smtp2goAPIClient(
            api_key="k", host="https://custom.api.com/v3/email/send"
        )
        assert client.host == "https://custom.api.com/v3/email/send"

    def test_repr_masks_api_key(self):
        """__repr__ should mask the middle of the API key."""
        client = Smtp2goAPIClient(api_key="abcdef12345678")
        r = repr(client)
        assert "Smtp2goAPIClient" in r
        assert "abcdef12345678" not in r  # full key should not appear
        assert "abcd" in r  # first 4 chars
        assert "5678" in r  # last 4 chars


# ── Send ─────────────────────────────────────────────────────────────────────


class TestSmtp2goAPIClientSend:
    """Tests for the send() method."""

    @patch("smtp2go_sendgrid.client.requests.post")
    def test_send_mail_object(self, mock_post):
        """Sending a Mail object posts the correct SMTP2GO payload."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": {"succeeded": 1}}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_post.return_value = mock_response

        client = Smtp2goAPIClient(api_key="test-key")
        mail = Mail(
            from_email="sender@example.com",
            to_emails="recipient@example.com",
            subject="Test",
            plain_text_content="Hello",
        )
        response = client.send(mail)

        assert isinstance(response, Response)
        assert response.status_code == 200
        assert "succeeded" in response.body

        call_kwargs = mock_post.call_args
        sent_json = call_kwargs.kwargs["json"]
        assert sent_json["api_key"] == "test-key"
        assert sent_json["sender"] == "sender@example.com"
        assert sent_json["to"] == ["recipient@example.com"]
        assert sent_json["subject"] == "Test"
        assert sent_json["text_body"] == "Hello"

    @patch("smtp2go_sendgrid.client.requests.post")
    def test_send_dict_payload(self, mock_post):
        """Sending a raw dict works and injects api_key."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": {"succeeded": 1}}'
        mock_response.headers = {}
        mock_post.return_value = mock_response

        client = Smtp2goAPIClient(api_key="test-key")
        raw = {
            "sender": "sender@example.com",
            "to": ["recipient@example.com"],
            "subject": "Raw Dict",
            "text_body": "Hello",
        }
        response = client.send(raw)

        call_kwargs = mock_post.call_args
        sent_json = call_kwargs.kwargs["json"]
        assert sent_json["api_key"] == "test-key"
        assert sent_json["sender"] == "sender@example.com"

    @patch("smtp2go_sendgrid.client.requests.post")
    def test_posts_to_correct_url(self, mock_post):
        """POST goes to the SMTP2GO v3/email/send endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{}"
        mock_response.headers = {}
        mock_post.return_value = mock_response

        client = Smtp2goAPIClient(api_key="test-key")
        mail = Mail(
            from_email="s@example.com",
            to_emails="r@example.com",
            subject="URL Test",
            plain_text_content="body",
        )
        client.send(mail)

        call_args = mock_post.call_args
        assert call_args.args[0] == "https://api.smtp2go.com/v3/email/send"

    @patch("smtp2go_sendgrid.client.requests.post")
    def test_posts_correct_headers(self, mock_post):
        """HTTP request includes Content-Type and Accept headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{}"
        mock_response.headers = {}
        mock_post.return_value = mock_response

        client = Smtp2goAPIClient(api_key="test-key")
        mail = Mail(
            from_email="s@e.com",
            to_emails="r@e.com",
            subject="T",
            plain_text_content="b",
        )
        client.send(mail)

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["Content-Type"] == "application/json"
        assert call_kwargs["headers"]["Accept"] == "application/json"

    @patch("smtp2go_sendgrid.client.requests.post")
    def test_timeout_is_set(self, mock_post):
        """HTTP request includes a timeout."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{}"
        mock_response.headers = {}
        mock_post.return_value = mock_response

        client = Smtp2goAPIClient(api_key="test-key")
        mail = Mail(
            from_email="s@e.com",
            to_emails="r@e.com",
            subject="T",
            plain_text_content="b",
        )
        client.send(mail)

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["timeout"] == 30

    @patch("smtp2go_sendgrid.client.requests.post")
    def test_response_wrapping(self, mock_post):
        """Error responses are wrapped correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "bad request"}'
        mock_response.headers = {"X-Foo": "bar"}
        mock_post.return_value = mock_response

        client = Smtp2goAPIClient(api_key="test-key")
        mail = Mail(
            from_email="s@example.com",
            to_emails="r@example.com",
            subject="Error Test",
            plain_text_content="body",
        )
        response = client.send(mail)

        assert response.status_code == 400
        assert response.body == '{"error": "bad request"}'
        assert response.headers["X-Foo"] == "bar"


# ── Response ─────────────────────────────────────────────────────────────────


class TestResponse:
    """Tests for the Response wrapper."""

    def test_attributes(self):
        r = Response(status_code=200, body="ok", headers={"X-A": "1"})
        assert r.status_code == 200
        assert r.body == "ok"
        assert r.headers == {"X-A": "1"}

    def test_default_headers(self):
        r = Response(status_code=200, body="ok")
        assert r.headers == {}

    def test_repr(self):
        r = Response(status_code=201, body="created")
        assert "201" in repr(r)
        assert "Response" in repr(r)


# ── Alias ────────────────────────────────────────────────────────────────────


class TestSendGridAlias:
    """Verify the SendGridAPIClient alias."""

    def test_alias_is_same_class(self):
        assert SendGridAPIClient is Smtp2goAPIClient
