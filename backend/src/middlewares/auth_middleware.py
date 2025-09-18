import firebase_admin
from firebase_admin import auth, firestore, credentials
from functools import wraps
from flask import request, jsonify

# Initialize Firebase app & Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "unauthorized", "message": "Authentication required"}), 401

        token = auth_header.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token["uid"]

            # 🔑 Fetch user doc from Firestore
            doc = db.collection("users").document(uid).get()
            print("Firestore user doc:", doc.to_dict())

            user_data = {"uid": uid, "email": decoded_token.get("email")}

            if doc.exists:
                user_data.update(doc.to_dict())

            request.user = user_data
            return fn(user=user_data, *args, **kwargs)

        except Exception as e:
            return jsonify({"error": "unauthorized", "message": str(e)}), 401

    return wrapper

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(user, *args, **kwargs):
            if "roles" not in user or not any(r in user["roles"] for r in roles):
                return jsonify({"error": "forbidden", "message": "Insufficient role"}), 403
            return fn(user=user, *args, **kwargs)
        return wrapper
    return decorator
