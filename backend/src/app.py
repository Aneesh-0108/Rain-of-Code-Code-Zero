from flask import Flask, jsonify, request
from src.config import settings
from src.errors import register_error_handlers, APIError
from src.decorators import require_auth, require_role
from src.services import events_service, registration_service



COL_EVENTS = "events"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    register_error_handlers(app)

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

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=settings.DEBUG, port=5001)