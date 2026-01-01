from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.utils.response_formatter import success_response, error_response

bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@bp.route("/search", methods=["GET"])
@jwt_required()
def search_user():
    """
    Search writers by ID or name (case-insensitive, partial match)
    Example: /api/v1/users/search?q=john
    """
    query = request.args.get("q", "").strip()
    if not query:
        return error_response("VALIDATION_ERROR", "Missing query parameter", status=400)

    # Return multiple writers that match
    writers = (
        User.query.filter(
            ((User.id.ilike(f"%{query}%")) | (User.full_name.ilike(f"%{query}%")))
            & (User.role == "writer")
        )
        .limit(10)
        .all()
    )

    if not writers:
        return error_response("NOT_FOUND", "No matching writers found", status=404)

    results = [
        {
            "id": u.id,
            "name": u.full_name,
            "email": u.email,
            "avatar": u.profile_image,
        }
        for u in writers
    ]

    return success_response({"results": results})
