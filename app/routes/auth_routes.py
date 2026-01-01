from flask import Blueprint, request, current_app
from app.services.auth_service import register_user, authenticate_user, generate_tokens_for_user
from app.utils.response_formatter import success_response, error_response
from app.extensions import db, jwt
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from app.utils.auth_utils import hash_password, check_password

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "writer")
    country = data.get("country")
    phone = data.get("phone")

    if not role in ("client", "writer"):
        return error_response("VALIDATION_ERROR", f"Could not register {role}", status=403)

    if not all([full_name, email, password]):
        return error_response("VALIDATION_ERROR", "Missing required fields", status=422)

    try:
        user = register_user(email, password, full_name, role=role, country=country)
        access, refresh = generate_tokens_for_user(user)
        return success_response({
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "application_status": user.application_status,
                "is_verified": user.is_verified,
            },
            "access_token": access,
            "refresh_token": refresh
        }, status=200)
    except Exception as e:
        return error_response("USER_REGISTER_ERROR", str(e), status=400)


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return error_response("VALIDATION_ERROR", "Missing fields", status=422)

    try:
        user = authenticate_user(email, password)
        access, refresh = generate_tokens_for_user(user)

        response_data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "application_status": getattr(user, "application_status", "not_applied"),
                "is_verified": getattr(user, "is_verified", False),
                "has_made_activation_deposit": getattr(user, "has_made_activation_deposit", False),
            },
            "access_token": access,
            "refresh_token": refresh,
        }

        return success_response(response_data)
    except Exception as e:
        print(f"error = {str(e)}")
        return error_response("AUTH_ERROR", "Invalid credentials", status=401)

@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    resp = success_response({"message": "Successfully logged out"})
    # unset cookies if you were using cookies; client should discard tokens.
    response, status = resp
    # NOTE: flask-jwt-extended provides helper to unset cookies if stored in cookies
    # Here we'll just return message; clients should delete tokens client-side
    return success_response({"message": "Successfully logged out"})

@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return error_response("NOT_FOUND", "User not found", status=404)

    return success_response(user.to_dict())


@bp.route("/verify-email", methods=["POST"])
def verify_email():
    token = request.json.get("token")

    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        user_id = decode_email_verification_token(token)
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.is_verified:
            return jsonify({"verified": True}), 200

        user.is_verified = True
        db.session.commit()

        return jsonify({"verified": True}), 200

    except Exception:
        return jsonify({
            "error": "Invalid or expired verification link"
        }), 400