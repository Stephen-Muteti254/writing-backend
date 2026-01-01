from flask import Blueprint, request
from app.services.leaderboard_service import get_leaderboard
from app.utils.response_formatter import success_response

bp = Blueprint("leaderboard", __name__, url_prefix="/api/v1")

@bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    period = request.args.get("period", "month")
    limit = int(request.args.get("limit", 50))
    lb = get_leaderboard(period=period, limit=limit)
    # For demo, current_user_rank left as sample; frontend can call /leaderboard and /me separately
    return success_response({"leaderboard": lb, "current_user_rank": None})
