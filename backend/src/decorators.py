from functools import wraps
from src.errors import APIError
import firebase_admin
from firebase_admin import auth
from flask import request
from .middlewares.auth_middleware import db 


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise APIError("Authentication required", 401, "unauthorized")

        token = auth_header.split(" ")[1]
        try:
            decoded = auth.verify_id_token(token)
        except Exception:
            raise APIError("Invalid or expired token", 401, "unauthorized")

        # Fetch roles from Firestore
        uid = decoded["uid"]
        user_doc = db.collection("users").document(uid).get()
        roles = user_doc.to_dict().get("roles", []) if user_doc.exists else []

        user = {
            "uid": uid,
            "email": decoded.get("email"),
            "roles": roles
        }

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

