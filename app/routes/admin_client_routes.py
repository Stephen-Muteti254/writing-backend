from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.order import Order
from app.utils.response_formatter import success_response, error_response

bp = Blueprint("admin_clients", __name__, url_prefix="/api/v1/admin/clients")

# ---- List all clients ----
@bp.route("", methods=["GET"])
@jwt_required()
def list_clients():
    # You can add an is_admin check here if you have roles
    search = request.args.get("search", "").strip().lower()

    q = User.query.filter(User.role == "client")
    if search:
        q = q.filter(
            db.or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.id.ilike(f"%{search}%"),
            )
        )

    clients = q.order_by(User.joined_at.desc()).all()

    results = []
    for c in clients:
        total_orders = Order.query.filter_by(client_id=c.id).count()
        total_spent = (
            db.session.query(db.func.sum(Order.client_budget))
            .filter(Order.client_id == c.id)
            .scalar()
            or 0
        )
        results.append({
            "id": c.id,
            "name": c.full_name,
            "email": c.email,
            "phone": getattr(c, "phone", None),
            "joinedDate": c.joined_at.strftime("%Y-%m-%d"),
            "totalOrders": total_orders,
            "totalSpent": total_spent,
            "status": "active" if c.is_verified else "suspended",
        })

    return success_response({"clients": results})


# ---- Suspend a client ----
@bp.route("/<client_id>/suspend", methods=["PATCH"])
@jwt_required()
def suspend_client(client_id):
    client = User.query.get(client_id)
    if not client or client.role != "client":
        return error_response("NOT_FOUND", "Client not found", status=404)

    client.is_verified = False
    db.session.commit()
    return success_response({"id": client.id, "status": "suspended"})


# ---- Activate a client ----
@bp.route("/<client_id>/activate", methods=["PATCH"])
@jwt_required()
def activate_client(client_id):
    client = User.query.get(client_id)
    if not client or client.role != "client":
        return error_response("NOT_FOUND", "Client not found", status=404)

    client.is_verified = True
    db.session.commit()
    return success_response({"id": client.id, "status": "active"})
