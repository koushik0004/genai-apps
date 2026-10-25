tools = [
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a Google Calendar event",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_time": {
                        "type": "string",
                        "description": "ISO 8601 date-time with timezone"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "ISO 8601 date-time with timezone"
                    },
                    "attendees": {                                                                                                            
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses to invite to the meeting"
                    },
                },
                "required": ["title", "start_time", "end_time"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

SYSTEM_PROMPT = (
    "You are a friendly calendar assistant. "
    "When the user asks to schedule something, use the calendar tool. "
    "Convert dates and times to ISO 8601 format with the America/Chicago timezone. "
    "If a needed detail (what, when, or how long) is missing, ask for it in one short question. "
    "When the user wants to schedule a meeting with someone, ask for or extract their email address so they can be invited as an attendee. Pass attendee emails to the calendar tool."
    "Never guess a missing date or time. Keep your replies short and friendly."
)

def get_system_prompt(timezone: str, current_time: str = None) -> str:
    time_ctx = f" Today's date and current time is {current_time}." if current_time else ""
    return (
        "You are a friendly calendar assistant. "
        "When the user asks to schedule something, use the calendar tool. "
        f"Convert dates and times to ISO 8601 format with the {timezone} timezone.{time_ctx} "
        "If a needed detail (what, when, or how long) is missing, ask for it in one short question. "
        "When the user wants to schedule a meeting with someone, ask for or extract their email address so they can be invited as an attendee. Pass attendee emails to the calendar tool."
        "Never guess a missing date or time. Keep your replies short and friendly."
    )