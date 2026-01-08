from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.utils.response_formatter import success_response, error_response
from sqlalchemy import or_, and_
from app.services.email_service import send_deposit_approved_email

bp = Blueprint("admin_writers", __name__, url_prefix="/api/v1/admin/writers")

def admin_required(user):
    return user and user.role == "admin"

@bp.route("", methods=["GET"])
@jwt_required()
def list_writers():
    uid = get_jwt_identity()
    admin = User.query.get(uid)
    if not admin_required(admin):
        return error_response("FORBIDDEN", "Admin privileges required", status=403)

    writers = User.query.filter(
        User.role == "writer",
        or_(
            User.application_status == "approved",
            User.application_status == "awaiting_initial_deposit"
        )
    ).all()

    data = [
        {
            "id": w.id,
            "email": w.email,
            "full_name": w.full_name,
            "rating": w.rating,
            "completed_orders": w.completed_orders,
            "total_earned": w.total_earned,
            "joined_at": w.joined_at.isoformat() if w.joined_at else None,
            "status": "active" if w.is_verified else "suspended-temporary",
            "account_status": w.account_status
        }
        for w in writers
    ]

    return success_response({"writers": data})


@bp.route("/<string:user_id>/approve-deposit", methods=["PATCH"])
@jwt_required()
def approve_deposit(user_id):
    uid = get_jwt_identity()
    admin = User.query.get(uid)
    if not admin_required(admin):
        return error_response("FORBIDDEN", "Admin privileges required", status=403)

    writer = User.query.get(user_id)
    if not writer:
        return error_response("NOT_FOUND", "Writer not found", 404)

    if writer.account_status not in ["awaiting_initial_deposit", "pending_verification"]:
        return error_response("INVALID_STATUS", f"Writer is currently '{writer.account_status}'", 400)

    writer.account_status = "active"
    writer.is_verified = True  # allow access to orders

    db.session.commit()

    # Send email notification
    send_deposit_approved_email(writer)

    return success_response({
        "message": "Writer deposit verified. Account activated.",
        "user_id": writer.id,
        "new_status": writer.account_status
    })
