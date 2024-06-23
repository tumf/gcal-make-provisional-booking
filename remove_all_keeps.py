from datetime import datetime
from main import delete_event, get_events 
from google_api_util import authenticate_google_api
from envvars import calendars, keep_event_calendar, keep_title

if __name__ == "__main__":
    credentials = authenticate_google_api()
    # check if calendars and keep_event_calendar are set
    if not calendars or not keep_event_calendar:
        print("CALENDARS and KEEP_EVENT_CALENDAR must be set")
        exit(1)

    credentials = authenticate_google_api()

    keep_events = [
        event
        for event in get_events(
            calendar_id=keep_event_calendar,
            credentials=credentials,
            query=keep_title,
            timeMin=datetime.min.isoformat() + "Z",
        )
        if event.get("summary") == keep_title
    ]

    for event in keep_events:
        delete_event(keep_event_calendar, event["id"], credentials)
