from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "securekey123"
ALGORITHM = "HS256"

def create_token(user):
    payload = {
        "user": user,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)