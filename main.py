from datetime import datetime, timedelta, date, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_events(
    calendar_id: str,
    credentials: Credentials,
    query: str = None,
    timeMin: str = None,
    timeMax: str = None,
) -> list:
    service = build("calendar", "v3", credentials=credentials)

    if timeMin is None:
        timeMin = datetime.min.isoformat() + "Z"
    if timeMax is None:
        timeMax = datetime.max.isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
            q=query,
        )
        .execute()
    )
    events = events_result.get("items", [])
    # Remove all-day events
    filtered_events = [event for event in events if "dateTime" in event["start"]]
    return filtered_events

def list_available_schedules(
    calendars: list,
    credentials: Credentials,
    from_date: date,
    to_date: date,
    duration_minutes: int = 60,
    from_hour: int = 0,
    to_hour: int = 23,
    unit_minutes: int = 30,
) -> list:

    available_slots = find_available_slots(
            from_date,
            to_date,
            calendars,
            credentials,
            from_hour,
            to_hour,
            duration_minutes,
            unit_minutes,
        )
    return available_slots


def get_combined_events(
    calendars: list, credentials: Credentials, date_from: datetime, date_to: datetime
) -> list:
    combined_events = []
    timeMin = date_from.isoformat() + "Z"
    timeMax = date_to.isoformat() + "Z"
    
    for calendar_id in calendars:
        events = get_events(calendar_id, credentials, timeMin=timeMin, timeMax=timeMax)
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            combined_events.append({"start_at": datetime.fromisoformat(start), "end_at": datetime.fromisoformat(end)})
    return combined_events


def get_time_slots(
    date_from: date, date_to: date, from_hour: int, to_hour: int, unit_minutes: int
) -> list:
    time_slots = []
    for day in range((date_to - date_from).days+1):
        day_date = date_from + timedelta(days=day)
        if day_date.weekday() in (5, 6):  # 5: Saturday, 6: Sunday
            continue
        current_time = datetime(day_date.year, day_date.month, day_date.day, from_hour, 0)
        end_time = datetime(day_date.year, day_date.month, day_date.day, to_hour, 0) - timedelta(minutes=unit_minutes)
        while current_time <= end_time:
            time_slots.append(current_time.replace(tzinfo=timezone.utc))
            current_time += timedelta(minutes=unit_minutes)
    return time_slots


def check_availability(
    start_time: datetime, combined_events: list, duration_minutes: int
) -> bool:
    end_time = start_time + timedelta(minutes=duration_minutes)
    for event in combined_events:
        # check if the event is overlapping with the time slot
        if max(start_time, event["start_at"]) < min(end_time, event["end_at"]):
            return False
    return True


def find_available_slots(
    date_from: date,
    date_to: date,
    calendars: list,
    credentials: Credentials,
    from_hour: int,
    to_hour: int,
    duration_minutes: int,
    unit_minutes: int,
) -> list:
    combined_events = get_combined_events(calendars, 
                                          credentials, 
                                          date_from.replace(hour=0, minute=0, second=0), 
                                          (date_to+timedelta(days=1)).replace(hour=0, minute=0, second=0))
    time_slots = get_time_slots(date_from, date_to, from_hour, to_hour, unit_minutes)
    available_slots = []

    for start_time in time_slots:
        if check_availability(start_time, combined_events, duration_minutes):
            end_time = start_time + timedelta(minutes=duration_minutes)
            available_slots.append(
                {
                    "start": start_time,
                    "end": end_time
                }
            )

    return available_slots


def insert_event(calendar_id: str, event: dict, credentials: Credentials) -> None:
    service = build("calendar", "v3", credentials=credentials)
    print("Inserting event:", event)
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')


def delete_event(calendar_id, event_id, credentials) -> None:
    service = build("calendar", "v3", credentials=credentials)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    print(f"Event deleted: {event_id}")


def remove_past_keep_events(
    calendar_id: str, credentials: Credentials, keep_title: str = "⛔️"
) -> bool:
    """
    Remove past keep events
    Return True if events were removed
    """
    updated = False

    keep_events = [
        event
        for event in get_events(
            calendar_id,
            credentials,
            query=keep_title,
            timeMin=datetime.min.isoformat() + "Z",
        )
        if event.get("summary") == keep_title
    ]

    for keep_event in keep_events:
        if (
            "dateTime" not in keep_event["start"]
            or "dateTime" not in keep_event["end"]
        ):
            continue
        keep_end_time = datetime.fromisoformat(keep_event["end"]["dateTime"])
        if keep_end_time < datetime.now().astimezone():
            delete_event(calendar_id, keep_event["id"], credentials)
            updated = True
    return updated
