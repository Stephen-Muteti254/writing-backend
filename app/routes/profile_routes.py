from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.utils.response_formatter import success_response, error_response

from sqlalchemy import func, desc
from app.models.review import Review
from app.models.order import Order
from app.models.writer_application import WriterApplication
from app.services.profile_service import build_leaderboard

bp = Blueprint("profile", __name__, url_prefix="/api/v1/profile")


def is_writer_profile_complete(user: User) -> tuple[bool, list[str]]:
    missing = []

    if not user.full_name:
        missing.append("full_name")
    if not user.bio:
        missing.append("bio")
    if not user.country:
        missing.append("country")
    if not user.profile_image:
        missing.append("profile_image")

    app = user.writer_application
    if not app:
        missing.append("application")
    else:
        if app.status != "approved":
            missing.append("application_approval")
        if not app.specialization:
            missing.append("specialization")
        if not app.years_experience:
            missing.append("years_experience")
        if not app.education:
            missing.append("education")
        if not app.cv_file_path:
            missing.append("cv")

    return len(missing) == 0, missing


@bp.route("", methods=["GET"])
@jwt_required()
def get_profile():
    uid = get_jwt_identity()
    u = User.query.get(uid)
    if not u:
        return error_response("NOT_FOUND", "User not found", status=404)

    is_complete, missing = is_writer_profile_complete(u)

    return success_response({
        "user": u.to_dict(),
        "profile_completion": {
            "is_complete": is_complete,
            "missing_fields": missing
        }
    })


@bp.route("", methods=["PATCH"])
@jwt_required()
def patch_profile():
    uid = get_jwt_identity()
    data = request.get_json() or {}
    u = User.query.get(uid)
    if not u:
        return error_response("NOT_FOUND", "User not found", status=404)
    if "full_name" in data:
        u.full_name = data.get("full_name")
    if "bio" in data:
        u.bio = data.get("bio")
    db.session.commit()
    return success_response({"id": u.id, "full_name": u.full_name, "bio": u.bio, "updated_at": u.joined_at.isoformat() + "Z"})

@bp.route("/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard():
    limit = int(request.args.get("limit", 50))
    results = build_leaderboard(limit)

    leaderboard = []
    for index, r in enumerate(results, start=1):
        leaderboard.append({
            "rank": index,
            "id": r.id,
            "name": r.full_name,
            "avatar": r.profile_image,
            "rating": round(float(r.rating), 2),
            "ordersCompleted": r.orders_completed,
            "successRate": 100.0,
            "specialization": r.specialization,
            "level": get_writer_level(index),
        })

    return success_response({"leaders": leaderboard})


@bp.route("/leaderboard/me", methods=["GET"])
@jwt_required()
def get_my_leaderboard_position():
    uid = get_jwt_identity()
    results = build_leaderboard()
    
    for index, r in enumerate(results, start=1):
        if r.id == uid:
            return success_response({
                "id": r.id,
                "rank": index,
                "rating": round(float(r.rating), 2),
                "ordersCompleted": r.orders_completed,
                "name": r.full_name,
            })

    return success_response({
        "rank": None,
        "rating": 0,
        "ordersCompleted": 0,
        "message": "User not ranked yet"
    })



def get_writer_level(rank: int) -> str | None:
    if rank == 1:
        return "Platinum Writer"
    if rank == 2:
        return "Gold Writer"
    if rank == 3:
        return "Silver Writer"
    return None
