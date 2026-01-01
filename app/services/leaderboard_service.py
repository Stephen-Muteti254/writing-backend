from app.models.user import User
from app.extensions import db

def get_leaderboard(period="month", limit=50):
    # Simple leaderboard sorted by total_earned
    users = User.query.order_by(User.total_earned.desc()).limit(limit).all()
    leaderboard = []
    rank = 1
    for user in users:
        leaderboard.append({
            "rank": rank,
            "writer": {"id": user.id, "name": user.full_name, "avatar": user.profile_image},
            "total_earned": float(user.total_earned),
            "orders_completed": user.completed_orders,
            "average_rating": float(user.rating),
            "success_rate": 100.0 if user.completed_orders > 0 else 0.0
        })
        rank += 1
    return leaderboard
