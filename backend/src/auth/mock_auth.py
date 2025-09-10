# Temporary mock auth (replace with real Firebase ID token verification)
def mock_current_user():
    # Return a deterministic fake user for dev until Auth team provides real verify
    return {
        "uid": "dev-user-123",
        "email": "dev@example.com",
        "roles": ["admin"]  # let you test protected endpoints early
    }