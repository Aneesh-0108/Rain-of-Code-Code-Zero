from functools import wraps
from src.errors import APIError
from src.auth.mock_auth import mock_current_user  # swap later

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = mock_current_user()
        if not user:
            raise APIError("Authentication required", 401, "unauthorized")
        return fn(user, *args, **kwargs)
    return wrapper

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(user, *args, **kwargs):
            if not any(r in user.get("roles", []) for r in roles):
                raise APIError("Forbidden", 403, "forbidden")
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator