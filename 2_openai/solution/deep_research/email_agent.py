from dotenv import load_dotenv
import os
from typing import Dict

#import sendgrid
#from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..")))
from smtp2go_sendgrid import Mail, Email, To, Content, SendGridAPIClient

load_dotenv(override=True)
TO_MAIL = os.getenv("TO_MAIL")
FROM_MAIL = os.getenv("FROM_MAIL")

@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body"""
    sg = SendGridAPIClient()
    from_email = Email(FROM_MAIL)  # put your verified sender here
    to_email = To(TO_MAIL)  # put your recipient here
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response", response.status_code)
    return "success"


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
