from datetime import datetime

ICAL_HEADER = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//HackathonEvents//EN"
ICAL_FOOTER = "END:VCALENDAR"

def format_dt(dt_str):
    # Expect dt_str as ISO string; if no 'Z', assume already suitable.
    # Simplify: remove separators -> YYYYMMDDTHHMMSSZ (ensuring Z)
    # More robust parsing could be added.
    if dt_str.endswith("Z"):
        base = dt_str.replace("-", "").replace(":", "").replace("Z", "")
        return f"{base}Z"
    # fallback naive
    clean = dt_str.replace("-", "").replace(":", "")
    if not clean.endswith("Z"):
        clean += "Z"
    return clean

def event_to_vevent(e: dict):
    uid = f"{e['id']}@hackathon.local"
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = format_dt(e["startTime"])
    dtend = format_dt(e["endTime"])
    summary = e["title"].replace("\n", " ")
    description = (e.get("description") or "").replace("\n", "\\n")
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{description}",
        # Placeholder URL
        f"URL:https://example.com/events/{e['id']}",
        "END:VEVENT"
    ]
    return "\n".join(lines)

def build_calendar(events: list[dict]):
    body_events = "\n".join(event_to_vevent(e) for e in events)
    return f"{ICAL_HEADER}\n{body_events}\n{ICAL_FOOTER}\n"