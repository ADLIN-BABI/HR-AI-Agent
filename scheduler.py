import os
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Paths (one level up from backend/)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service(auth_type="service", delegated_user=None):
    """
    Return Google Calendar service using either:
      - Service account (default)
      - OAuth user consent (if auth_type="oauth")
    """
    creds = None

    if auth_type == "service":
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=SCOPES
        )
        if delegated_user:
            creds = creds.with_subject(delegated_user)

    elif auth_type == "oauth":
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
    else:
        raise ValueError("auth_type must be 'oauth' or 'service'")

    return build("calendar", "v3", credentials=creds)


def create_event(service, calendar_id="primary", summary="Interview",
                 description="", start_dt=None, end_dt=None,
                 timezone="Asia/Kolkata", attendees_emails=None, location=None):
    """Create a calendar event."""
    if start_dt is None:
        start_dt = datetime.now() + timedelta(hours=1)
    if end_dt is None:
        end_dt = start_dt + timedelta(minutes=30)

    if start_dt.tzinfo is None:
        start_dt = pytz.timezone(timezone).localize(start_dt)
    if end_dt.tzinfo is None:
        end_dt = pytz.timezone(timezone).localize(end_dt)

    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
        "attendees": [{"email": e} for e in (attendees_emails or [])],
        "reminders": {"useDefault": True},
    }
    return service.events().insert(calendarId=calendar_id, body=event, sendUpdates="all").execute()


def list_events(service, calendar_id="primary", max_results=10):
    """List upcoming events."""
    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(calendarId=calendar_id, timeMin=now,
              maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    return events_result.get("items", [])


def update_event(service, event_id, calendar_id="primary", updated_fields=None):
    """Update an existing event."""
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    if updated_fields:
        event.update(updated_fields)
    return service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()


def delete_event(service, event_id, calendar_id="primary"):
    """Delete an event."""
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return True
