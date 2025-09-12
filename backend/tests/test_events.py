from src.services import events_service

def test_create_event_route(client, monkeypatch):
    def fake_create(data, uid):
        return "ABC123", {
            "title": data["title"],
            "startTime": data["startTime"],
            "endTime": data["endTime"],
            "capacity": data["capacity"],
            "registeredCount": 0,
            "status": "pending",
            "createdBy": uid,
            "createdAt": "2025-01-01T00:00:00Z"
        }
    monkeypatch.setattr(events_service, "create_event", fake_create)
    payload = {
        "title": "Test",
        "startTime": "2025-01-02T10:00:00Z",
        "endTime": "2025-01-02T11:00:00Z",
        "capacity": 10
    }
    # Because require_auth uses mock user, direct call works
    resp = client.post("/api/events", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Test"
    assert data["status"] == "pending"