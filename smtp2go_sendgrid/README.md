# smtp2go_sendgrid

A drop-in replacement for the [SendGrid Python SDK](https://github.com/sendgrid/sendgrid-python) that sends emails via the [SMTP2GO API](https://developers.smtp2go.com/docs/introduction-guide).

Change your import and API key — everything else stays the same.

## Quick Start

### Before (SendGrid)

```python
import sendgrid
from sendgrid.helpers.mail import Mail, From, To, Content

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
mail = Mail(
    from_email=From("sender@example.com", "Sender"),
    to_emails=To("recipient@example.com"),
    subject="Hello from SendGrid",
    plain_text_content="This is a test email.",
)
response = sg.send(mail)
```

### After (SMTP2GO — one-line change)

```python
from smtp2go_sendgrid import Smtp2goAPIClient, Mail, From, To, Content

sg = Smtp2goAPIClient(api_key=os.environ.get("SMTP2GO_API_KEY"))
mail = Mail(
    from_email=From("sender@example.com", "Sender"),
    to_emails=To("recipient@example.com"),
    subject="Hello from SMTP2GO",
    plain_text_content="This is a test email.",
)
response = sg.send(mail)
print(response.status_code)
print(response.body)
```

If you want a true drop-in alias:

```python
from smtp2go_sendgrid import SendGridAPIClient  # same class, different name
```

## Features

| Feature | Supported |
|---|:---:|
| Plain text email | ✅ |
| HTML email | ✅ |
| Multiple recipients (To/CC/BCC) | ✅ |
| Named recipients (`Name <email>`) | ✅ |
| Attachments (base64) | ✅ |
| Custom headers | ✅ |
| Reply-To | ✅ |
| Template ID + template data | ✅ |
| Tuple / string / helper class inputs | ✅ |

## API Reference

### Helper Classes

All helpers mirror their SendGrid equivalents:

- `Email(email, name=None)`
- `From(email, name=None)`, `To(email, name=None)`, `Cc(email, name=None)`, `Bcc(email, name=None)`
- `Content(mime_type, value)` — accepts `MimeType.text`, `MimeType.html`, or strings
- `Subject(subject)`
- `Header(key, value)`
- `ReplyTo(email, name=None)`
- `Attachment(file_content, file_name, file_type=None)`
  - `Attachment.from_file(path)` — convenience method to read and encode a local file

### Mail

```python
mail = Mail(
    from_email=None,     # From, Email, str, tuple
    to_emails=None,      # To, Email, str, tuple, list
    subject=None,        # Subject, str
    plain_text_content=None,  # Content, str
    html_content=None,   # Content, str
)
```

Methods: `add_to()`, `add_cc()`, `add_bcc()`, `add_content()`, `add_attachment()`, `add_header()`

Properties: `from_email`, `subject`, `to`, `cc`, `bcc`, `reply_to`, `template_id`, `dynamic_template_data`

### Smtp2goAPIClient

```python
client = Smtp2goAPIClient(api_key=None)  # falls back to SMTP2GO_API_KEY env var
response = client.send(mail)
```

### Response

- `response.status_code` — HTTP status code
- `response.body` — response body as string
- `response.headers` — response headers as dict

## Running Tests

```bash
uv run python -m pytest smtp2go_sendgrid/tests/ -v
```
