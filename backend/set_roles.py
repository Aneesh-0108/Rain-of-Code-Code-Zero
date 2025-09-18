from firebase_admin import auth
from src.middleware.auth_middleware import db   # or wherever db is defined


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "serviceAccountKey.json")

cred = credentials.Certificate(json_path)
firebase_admin.initialize_app(cred)

# Replace UID with your actual Firebase UID
uid = "7SDyLgDu9cMkvhPi0au6T7kgyHm1"

auth.set_custom_user_claims(uid, {"roles": ["admin"]})
print(f" Roles set for UID {uid}")
