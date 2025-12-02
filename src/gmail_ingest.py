from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only scope, so we cannot accidentally delete/modify emails
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    """
    Returns an authenticated Gmail API service object.
    On first run, opens a browser window for you to log in and grant access.
    Stores refresh token in token.json for subsequent runs.
    """
    creds = None

    # token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token
            creds.refresh(Request())
        else:
            # Run local server for OAuth
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def list_recent_emails(max_results: int = 20):
    """
    Lists some basic info (date, from, subject) for the most recent emails in INBOX.
    """
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results,
    ).execute()

    messages = results.get("messages", [])

    print(f"Found {len(messages)} messages")
    for msg in messages:
        msg_detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg_detail["payload"]["headers"]}
        subject = headers.get("Subject", "(no subject)")
        from_addr = headers.get("From", "")
        date = headers.get("Date", "")

        print(f"- {date} | {from_addr} | {subject}")


if __name__ == "__main__":
    list_recent_emails(20)
