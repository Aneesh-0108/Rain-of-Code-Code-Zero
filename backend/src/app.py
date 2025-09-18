from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from functools import wraps

# use relative imports since everything is inside src/
from .config import settings
from .errors import register_error_handlers, APIError
from .decorators import require_auth, require_role
from .services import events_service, registration_service
from .utils.ics import build_calendar

import os


COL_EVENTS = "events"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    register_error_handlers(app)

    # CORS config for local frontend
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000"
    ]}})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/events")
    def list_events():
        return jsonify(events_service.list_approved_events())

    @app.post("/api/events")
    @require_auth
    @require_role("admin", "organizer")
    def create_event(user):
        data = request.get_json(force=True)
        eid, payload = events_service.create_event(data, user["uid"])
        return jsonify({"id": eid, **payload}), 201

    @app.post("/api/events/<event_id>/register")
    @require_auth
    def register_event(user, event_id):
        registration_service.register_user(event_id, user["uid"])
        return jsonify({"status": "registered"})

    @app.delete("/api/events/<event_id>/register")
    @require_auth
    def cancel_registration(user, event_id):
        registration_service.cancel_registration(event_id, user["uid"])
        return jsonify({"status": "canceled"})

    @app.post("/api/events/<event_id>/approve")
    @require_auth
    @require_role("admin")
    def approve_event(user, event_id):
        events_service.approve_event(event_id)
        return jsonify({"status": "approved"})

    @app.get("/api/me")
    @require_auth
    def me(user):
        return jsonify({
            "uid": user["uid"],
            "email": user.get("email"),
            "roles": user.get("roles", [])
        })

    @app.get("/api/events.ics")
    def events_ics():
        # Export approved events only
        events = events_service.list_approved_events()
        data = build_calendar(events)
        return Response(data, mimetype="text/calendar; charset=utf-8")

    @app.get("/api/events/<event_id>.ics")
    def event_ics(event_id):
        # Fetch single event
        all_e = events_service.list_approved_events()
        match = next((e for e in all_e if e["id"] == event_id), None)
        if not match:
            return Response("Event not found", status=404)
        data = build_calendar([match])
        return Response(data, mimetype="text/calendar; charset=utf-8")

    @app.get("/debug/events")
    def debug_events():
        events = events_service.list_approved_events()
        return jsonify([e["id"] for e in events])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=settings.DEBUG, port=5001)
