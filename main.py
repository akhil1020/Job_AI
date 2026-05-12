from __future__ import print_function
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

def authenticate():
    creds = None

    try:
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )
    except:
        pass

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

def send_email(service):
    message = MIMEText("Hello from AI Job Agent!")

    message["to"] = "akhilpatoliya1020@gmail.com"
    message["subject"] = "Test Email"

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    body = {
        "raw": raw
    }

    service.users().messages().send(
        userId="me",
        body=body
    ).execute()

    print("Email sent!")

if __name__ == "__main__":
    service = authenticate()
    send_email(service)