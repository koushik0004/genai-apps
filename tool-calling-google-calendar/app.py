"""
A simple chatbot-style web UI for the calendar assistant.

Run it with:
    python app.py
then open  http://127.0.0.1:5000  in your browser.

How it works:
  * Serves the chat page (templates/index.html).
  * Talks to the same AI as calendar_assistant.py.
  * When the AI asks to create an event, it creates it in your Google
    Calendar and tells the page about the result.

The command-line version (calendar_assistant.py) still works too - pick
whichever you prefer.
"""

from datetime import datetime
import json

from flask import Flask, render_template, request, jsonify

from authenticate import get_calendar_service
from utility import get_system_prompt, tools as TOOLS
from lib import timer, client, GEMINI_GEMMA_MODEL

service = None

def get_service():
    """
        Connect to Google Calendar on first use (opens a browser to sign in).
    """
    global service
    if service is None:
        service = get_calendar_service()
    
    return service

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

def create_calendar_event(title, start_time, end_time, attendees=None):
    """
        Create a real event in your Google Calendar and return its details.
    """
    event = {
        "summary": title,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }
    if attendees:
        event['attendees'] = [{"email": email.strip()} for email in attendees if email.strip()]

    # return get_service().events().insert(calendarId="primary", body=event).execute()
    return get_service().events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all" # Sends Google Calendar invite to attendees
    ).execute()

SYSTEM_PROMPT = (
    "You are a friendly calendar assistant. "
    "When the user asks to schedule something, use the calendar tool. "
    "Convert dates and times to ISO 8601 format with the America/Chicago timezone. "
    "If a needed detail (what, when, or how long) is missing, ask for it in one short question. "
    "When the user wants to schedule a meeting with someone, ask for or extract their email address so they can be invited as an attendee. Pass attendee emails to the calendar tool."
    "Never guess a missing date or time. Keep your replies short and friendly."
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("messages") or []
    timezone = data.get("timezone") or str(datetime.now().astimezone().tzinfo)

    if not user_message:
        return jsonify({"error": "Please type what you'd like to schedule."}), 400

    # Build the message list: instructions, then the recent conversation,
    # then the user's new message.
    messages = [{"role": "system", "content": get_system_prompt(timezone, str(datetime.now()))}]
    messages += history[-20:]  # keep only the last 20 turns so the list stays small
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=GEMINI_GEMMA_MODEL,
        messages=messages,
        tools=TOOLS
    )
    message = response.choices[0].message
    reply = (message.content or "").strip()

    # Did the AI decide to create an event?
    event = None
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "create_calendar_event":
                args = json.loads(tool_call.function.arguments)
                try:
                    result = create_calendar_event(**args)
                    event = {
                        "title": args.get("title"),
                        "start": args.get("start_time"),
                        "end": args.get("end_time"),
                        "link": result.get("htmlLink"),
                    }
                    reply = "Done! ✅ Your event is on the calendar - go check it."
                except Exception as exc:
                    # surface a friendly, readable error
                    reply = f"I tried to create that event, but Google Calendar said: {exc}"

    return jsonify({"reply": reply, "event": event})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    # host="0.0.0.0" makes the server accessible inside Docker and across network
    # debug=True enables auto-reloading whenever python files are modified
    app.run(debug=True, host="0.0.0.0", port=port)