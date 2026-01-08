from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_email_verification_token(user_id: int) -> str:
    s = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
    return s.dumps({"user_id": user_id}, salt="email-verify")

def decode_email_verification_token(token: str) -> int:
    s = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
    data = s.loads(
        token,
        salt="email-verify",
        max_age=current_app.config["EMAIL_VERIFY_EXPIRES"]
    )
    return data["user_id"]
