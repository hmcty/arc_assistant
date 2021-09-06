import sys
import datetime
import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

TIMEZONE_LEN = 6


def construct_calendar_msg(calendar_event):
    """
    Transforms Google Calendar response to Discord-ready message.
    Format options (varies by response):
        - Event name\n Aug 02
        - Event name\n Aug 02 - Aug 03
        - Event name\n Aug 02 02:00 PM to 03:00 PM
        - Event name\n Aug 02 2:00 PM to Aug 03 3:00 PM
    Event name is embedded with Google Calendar link.
    """

    if 'date' in calendar_event['start']:
        # Convert date strings to datetime objects
        start_date = datetime.strptime(
            calendar_event['start']['date'],
            '%Y-%m-%d'
        )
        end_date = datetime.strptime(
            calendar_event['end']['date'],
            '%Y-%m-%d'
        )

        # List first day
        date_msg = datetime.strftime(
            start_date, "%b %d "
        )

        # If event lasts more than one day, state range
        if start_date.date() != end_date.date():
            date_msg += datetime.strftime(
                end_date, "to %b %d"
            )
    else:
        # Convert date strings to datetime objects
        start_datetime = datetime.strptime(
            calendar_event['start']['dateTime'][:-TIMEZONE_LEN],
            '%Y-%m-%dT%H:%M:%S'
        )
        end_datetime = datetime.strptime(
            calendar_event['end']['dateTime'][:-TIMEZONE_LEN],
            '%Y-%m-%dT%H:%M:%S'
        )

        # List first day
        date_msg = datetime.strftime(
            start_datetime, "%b %d from %I:%M %p "
        )

        # If event lasts more than one day, append date end-point
        if start_datetime.date() != end_datetime.date():
            date_msg += datetime.strftime(
                end_datetime, "to %b %d %I:%M %p"
            )
        else:
            date_msg += datetime.strftime(
                end_datetime, "to %I:%M %p"
            )

    # Create embedded message
    msg = discord.Embed()
    msg.description = '[{name}]({event_url})\n {date_msg}'.format(
        name=calendar_event['summary'],
        event_url=calendar_event['htmlLink'],
        date_msg=date_msg
    )
    return msg


def create_service():
    """Initilizes Google Service account from env json"""
    info = json.loads("config.json")["google_service"]
    creds = service_account.Credentials.from_service_account_info(info)
    return build('calendar', 'v3', credentials=creds)


def collect_today(calendar_id):
    """
    Gets events within 24 hours of current time.
    """
    print("Parsing date")
    start = datetime.datetime.utcnow()
    end = start + datetime.timedelta(1)

    print("Obtaining and returing events")
    events_result = create_service().events().list(calendarId=calendar_id,
                                                   timeMin=start.isoformat() + 'Z',
                                                   timeMax=end.isoformat() + 'Z',
                                                   singleEvents=True,
                                                   orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def collect_week(calendar_id):
    """
    Collects n google calendar events within a week of current time.
    """
    print("Parsing date")
    start = datetime.datetime.utcnow()
    end = start + datetime.timedelta(week=1)

    print("Obtaining and returing events")
    events_result = create_service().events().list(calendarId=calendar_id,
                                                   timeMin=start.isoformat() + 'Z',
                                                   timeMax=end.isoformat() + 'Z',
                                                   singleEvents=True,
                                                   orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events