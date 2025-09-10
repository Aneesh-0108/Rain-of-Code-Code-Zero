from src.firebase_init import db
from src.errors import APIError

COL_EVENTS = "events"
COL_REGS = "registrations"

def register_user(event_id, user_uid):
    event_ref = db.collection(COL_EVENTS).document(event_id)
    event_snap = event_ref.get()
    if not event_snap.exists:
        raise APIError("Event not found", 404, "not_found")
    event = event_snap.to_dict()
    if event["status"] != "approved":
        raise APIError("Event not open", 400, "not_open")

    reg_id = f"{event_id}_{user_uid}"
    reg_ref = db.collection(COL_REGS).document(reg_id)
    if reg_ref.get().exists:
        raise APIError("Already registered", 409, "duplicate")
    # (Will be transactional later)
    if event["registeredCount"] >= event["capacity"]:
        raise APIError("Event full", 409, "full")

    # Update counts and create registration (NOT SAFE under concurrency yet)
    event_ref.update({"registeredCount": event["registeredCount"] + 1})
    reg_ref.set({"eventId": event_id, "userId": user_uid})

def cancel_registration(event_id, user_uid):
    reg_id = f"{event_id}_{user_uid}"
    reg_ref = db.collection(COL_REGS).document(reg_id)
    if not reg_ref.get().exists:
        raise APIError("Not registered", 404, "not_registered")

    event_ref = db.collection(COL_EVENTS).document(event_id)
    ev_snap = event_ref.get()
    if ev_snap.exists:
        ev = ev_snap.to_dict()
        if ev["registeredCount"] > 0:
            event_ref.update({"registeredCount": ev["registeredCount"] - 1})
    reg_ref.delete()