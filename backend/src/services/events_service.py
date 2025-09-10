"""
Event Document Schema (Firestore collection: events)
Fields:
- title (str)
- description (str)
- startTime (ISO8601 string UTC)
- endTime (ISO8601 string UTC)
- capacity (int)
- registeredCount (int) - maintained by registration operations
- status (str) one of: pending, approved
- createdBy (uid string)
- createdAt (ISO8601 string)
"""
from datetime import datetime
from src.firebase_init import db
from src.errors import APIError

COL_EVENTS = "events"

def create_event(data, user_uid: str):
    required = ["title", "startTime", "endTime", "capacity"]
    for f in required:
        if f not in data:
            raise APIError(f"Missing field: {f}", 422, "validation_error")

    doc_ref = db.collection(COL_EVENTS).document()
    payload = {
        "title": data["title"],
        "description": data.get("description", ""),
        "startTime": data["startTime"],
        "endTime": data["endTime"],
        "capacity": int(data["capacity"]),
        "registeredCount": 0,
        "status": "pending",
        "createdBy": user_uid,
        "createdAt": datetime.utcnow().isoformat()
    }
    doc_ref.set(payload)
    return doc_ref.id, payload

def list_approved_events():
    q = db.collection(COL_EVENTS).where("status", "==", "approved").order_by("startTime")
    return [s.to_dict() | {"id": s.id} for s in q.stream()]