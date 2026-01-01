from app.extensions import db
from app.models.user import User
from app.utils.auth_utils import hash_password, check_password
from app.utils.exceptions import ServiceError
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from flask import current_app

def register_user(email, password, full_name, role="client", country=None):
    if User.query.filter_by(email=email).first():
        raise ServiceError(
            code="USER_EXISTS",
            message="User with that email already exists",
            details={"field": "email"}
        )

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        country=country
    )
    db.session.add(user)
    db.session.commit()
    return user

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password_hash):
        raise ServiceError(code="AUTH_FAILED", message="Invalid credentials")
    return user

def generate_tokens_for_user(user):
    access = create_access_token(identity=user.id, expires_delta=timedelta(seconds=current_app.config.get("ACCESS_EXPIRES", 86400)))
    refresh = create_refresh_token(identity=user.id, expires_delta=timedelta(seconds=current_app.config.get("REFRESH_EXPIRES", 86400)))
    return access, refresh
