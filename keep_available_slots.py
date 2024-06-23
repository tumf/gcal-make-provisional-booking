from datetime import datetime, timedelta
import random
from main import (
    get_events,
    list_available_schedules,
    insert_event,
    remove_past_keep_events,
)
from google_api_util import authenticate_google_api
from envvars import calendars, keep_event_calendar, from_hour, to_hour, duration_minutes, unit_minutes, min_slots, keep_recent_week_count, keep_over_week_count, keep_title

def check_overlapping_events(event: dict, events: list[dict]) -> bool:  
    for e in events:
        if max(event["start"], e["start"]) < min(event["end"], e["end"]):
            return True
    return False

if __name__ == "__main__":

    # check if calendars and keep_event_calendar are set
    if not calendars or not keep_event_calendar:
        print("CALENDARS and KEEP_EVENT_CALENDAR must be set")
        exit(1)

    credentials = authenticate_google_api()
    remove_past_keep_events(calendar_id=keep_event_calendar, credentials=credentials, keep_title=keep_title)

    # 14 days
    for day in range(14):
        target_date = (datetime.now() + timedelta(days=day + 1)).replace(
            hour=0, minute=0, second=0
        )
        keep_events = get_events(
            keep_event_calendar,
            credentials,
            query=keep_title,
            timeMin=target_date.isoformat() + "Z",
            timeMax=(target_date + timedelta(days=1)).isoformat() + "Z",
        )

        slots = list_available_schedules(
            calendars=calendars,
            credentials=credentials,
            from_date=target_date,
            to_date=target_date,
            duration_minutes=duration_minutes,
            from_hour=from_hour,  # utc
            to_hour=to_hour,  # utc
            unit_minutes=unit_minutes,
        )
        if len(slots) < min_slots:
            continue

        if day <= 7:
            # create 8 keep events in recent 7 days
            num_keep_events = keep_recent_week_count - len(keep_events)
        else:
            # create 4 keep events over 7 days
            num_keep_events = keep_over_week_count - len(keep_events)

        if num_keep_events > 0:
            selected_slots = []
            while len(selected_slots) < num_keep_events:
                available_slots = [
                    s
                    for s in slots
                    if s not in selected_slots
                    and not check_overlapping_events(s, selected_slots)
                ]
                if not len(available_slots) > 0:
                    break
                random_slot = random.choice(available_slots)
                selected_slots.append(random_slot)

            for slot in selected_slots:
                print(slot)
                event = {
                    "summary": keep_title,
                    "start": {"dateTime": slot["start"].isoformat()},
                    "end": {"dateTime": slot["end"].isoformat()},
                }
                insert_event(keep_event_calendar, event, credentials)
