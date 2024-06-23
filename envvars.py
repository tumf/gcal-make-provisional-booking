import os

calendars = os.getenv("CALENDARS").split(',')
keep_event_calendar = os.getenv("KEEP_EVENT_CALENDAR")
from_hour = int(os.getenv("FROM_HOUR", "1"))
to_hour = int(os.getenv("TO_HOUR", "11"))
duration_minutes = int(os.getenv("DURATION_MINUTES", "30"))
unit_minutes = int(os.getenv("UNIT_MINUTES", "30"))
min_slots = int(os.getenv("MIN_SLOTS", "10"))
keep_recent_week_count = int(os.getenv("KEEP_RECENT_WEEK_COUNT", "8"))
keep_over_week_count = int(os.getenv("KEEP_OVER_WEEK_COUNT", "4"))
keep_title = os.getenv("KEEP_TITLE", "⛔️")
