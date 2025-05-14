import bcrypt
from itsdangerous import URLSafeTimedSerializer
from app.config import SECRET_KEY

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(email: str) -> str:
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email)

def verify_token(token: str, max_age=3600) -> str:
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        return s.loads(token, max_age=max_age)
    except Exception:
        return None