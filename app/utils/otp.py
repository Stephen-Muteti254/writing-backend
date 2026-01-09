import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"

def hash_otp(otp: str):
    return generate_password_hash(otp)

def verify_otp(otp: str, otp_hash: str):
    return check_password_hash(otp_hash, otp)

def otp_expiry(minutes=5):
    return datetime.utcnow() + timedelta(minutes=minutes)
