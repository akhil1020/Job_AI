from __future__ import print_function

import os
import base64
import mimetypes

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


# ---------------- AUTH ---------------- #

def authenticate():

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "desktop_credential.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


from langchain_core.tools import tool

@tool
def send_email_tool(
    to_email: str,
    subject: str,
    body_text: str,
    file_path: str = "resume.pdf"
) -> str:
    """
    Sends an email with attachment using Gmail API.

    Args:
        to_email: recipient email address
        subject: email subject
        body_text: email content
        file_path: path to attachment file (PDF/DOC)

    Returns:
        Success message
    """
    if not os.path.exists(file_path):
        return f"Attachment not found: {file_path}"

    service = authenticate()

    message = MIMEMultipart()
    message["to"] = to_email
    message["subject"] = subject

    message.attach(MIMEText(body_text, "plain"))

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    main_type, sub_type = content_type.split("/")

    with open(file_path, "rb") as f:
        attachment = MIMEBase(main_type, sub_type)
        attachment.set_payload(f.read())

    encoders.encode_base64(attachment)

    attachment.add_header(
        "Content-Disposition",
        f'attachment; filename="{file_path}"'
    )

    message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    return f"Email sent to {to_email}"
