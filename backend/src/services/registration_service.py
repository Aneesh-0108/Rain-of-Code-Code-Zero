from src.firebase_init import db
from src.errors import APIError
from google.cloud import firestore   # ✅ import this

COL_EVENTS = "events"
COL_REGS = "registrations"

# ---------------------------
# Register User
# ---------------------------
@firestore.transactional
def _register_user_txn(transaction, event_id, user_uid):
    event_ref = db.collection(COL_EVENTS).document(event_id)
    reg_ref = db.collection(COL_REGS).document(f"{event_id}_{user_uid}")

    ev_snap = event_ref.get(transaction=transaction)
    if not ev_snap.exists:
        raise APIError("Event not found", 404, "not_found")

    ev = ev_snap.to_dict()
    if ev["status"] != "approved":
        raise APIError("Event not open", 400, "not_open")

    if ev["registeredCount"] >= ev["capacity"]:
        raise APIError("Event full", 409, "full")

    reg_snap = reg_ref.get(transaction=transaction)
    if reg_snap.exists:
        raise APIError("Already registered", 409, "duplicate")

    transaction.update(event_ref, {"registeredCount": ev["registeredCount"] + 1})
    transaction.set(reg_ref, {"eventId": event_id, "userId": user_uid})


def register_user(event_id, user_uid):
    transaction = db.transaction()
    return _register_user_txn(transaction, event_id, user_uid)


# ---------------------------
# Cancel Registration
# ---------------------------
@firestore.transactional
def _cancel_registration_txn(transaction, event_id, user_uid):
    event_ref = db.collection(COL_EVENTS).document(event_id)
    reg_ref = db.collection(COL_REGS).document(f"{event_id}_{user_uid}")

    reg_snap = reg_ref.get(transaction=transaction)
    if not reg_snap.exists:
        raise APIError("Not registered", 404, "not_registered")

    ev_snap = event_ref.get(transaction=transaction)
    if ev_snap.exists:
        ev = ev_snap.to_dict()
        if ev["registeredCount"] > 0:
            transaction.update(event_ref, {
                "registeredCount": ev["registeredCount"] - 1
            })

    transaction.delete(reg_ref)


def cancel_registration(event_id, user_uid):
    transaction = db.transaction()
    return _cancel_registration_txn(transaction, event_id, user_uid)
