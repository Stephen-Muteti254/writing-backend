from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.payment_service import get_balance_for_user, create_withdrawal
from app.models.user import User
from app.utils.response_formatter import success_response, error_response
from app.models.payment_method import PaymentMethod
from app.extensions import db

bp = Blueprint("payments", __name__, url_prefix="/api/v1")

@bp.route("/balance", methods=["GET"])
@jwt_required()
def balance():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return error_response("NOT_FOUND", "User not found", status=404)
    bal = get_balance_for_user(user)
    return success_response(bal)

@bp.route("/transactions", methods=["GET"])
@jwt_required()
def transactions():
    from app.models.transaction import Transaction
    uid = get_jwt_identity()
    ttype = request.args.get("type")
    page = int(request.args.get("page",1))
    limit = int(request.args.get("limit",20))

    q = Transaction.query.filter_by(user_id=uid)

    # EXCLUDE withdrawals if you want separate tab
    q = q.filter(Transaction.type == "withdrawal")

    if ttype:
        q = q.filter_by(type=ttype)

    total = q.count()
    items = q.order_by(Transaction.created_at.desc()).offset((page-1)*limit).limit(limit).all()

    txns = []
    for t in items:
        txns.append({
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "description": t.description,
            "status": t.status,
            "order_id": t.order_id,
            "created_at": t.created_at.isoformat() + "Z"
        })

    pagination = {"total": total, "page": page, "limit": limit, "total_pages": (total + limit-1)//limit}
    return success_response({"transactions": txns, "pagination": pagination})

@bp.route("/withdrawals", methods=["POST"])
@jwt_required()
def withdraw():
    data = request.get_json() or {}
    amount = data.get("amount")
    method = data.get("payment_method")
    details = data.get("payment_details")

    if not amount or not method or not details:
        return error_response("VALIDATION_ERROR", "Amount, method and details are required")

    uid = get_jwt_identity()

    try:
        txn = create_withdrawal(uid, amount, method, details)
    except Exception as e:
        print(f"error = {str(e)}")
        return error_response("NO_PAYMENT_METHOD", str(e), status=400)

    return success_response({
        "id": txn.id,
        "amount": txn.amount,
        "status": txn.status,
        "created_at": txn.created_at.isoformat() + "Z"
    }, status=201)


@bp.route("/withdrawals", methods=["GET"])
@jwt_required()
def list_withdrawals():
    from app.models.transaction import Transaction

    uid = get_jwt_identity()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    q = Transaction.query.filter_by(user_id=uid, type="withdrawal")

    # Optional filters
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    if date_from:
        q = q.filter(Transaction.created_at >= date_from)
    if date_to:
        q = q.filter(Transaction.created_at <= date_to)

    total = q.count()
    items = (
        q.order_by(Transaction.created_at.desc())
         .offset((page - 1) * limit)
         .limit(limit)
         .all()
    )

    return success_response({
        "withdrawals": [
            {
                "id": t.id,
                "amount": t.amount,
                "status": t.status,
                "created_at": t.created_at.isoformat() + "Z"
            } for t in items
        ],
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    })


@bp.route("/payment-methods", methods=["POST"])
@jwt_required()
def add_payment_method():
    from app.models.payment_method import PaymentMethod

    data = request.get_json() or {}
    print(f"incoming data = {data}")
    method = data.get("method")
    details = data.get("details")
    is_default = data.get("is_default", False)

    if not method or not details:
        return error_response("VALIDATION_ERROR", "Method and details are required")

    uid = get_jwt_identity()

    # If default: unset other defaults
    if is_default:
        PaymentMethod.query.filter_by(user_id=uid, is_default=True).update({"is_default": False})

    pm = PaymentMethod(
        user_id=uid,
        method=method,
        details=details,
        is_default=is_default
    )

    db.session.add(pm)
    db.session.commit()

    return success_response({"id": pm.id}, "Payment method added", status=201)


@bp.route("/payment-methods/<pm_id>/default", methods=["PATCH"])
@jwt_required()
def set_default(pm_id):
    from app.models.payment_method import PaymentMethod
    uid = get_jwt_identity()

    pm = PaymentMethod.query.filter_by(id=pm_id, user_id=uid).first()
    if not pm:
        return error_response("NOT_FOUND", "Payment method not found", status=404)

    # Reset defaults
    PaymentMethod.query.filter_by(user_id=uid).update({"is_default": False})

    pm.is_default = True
    db.session.commit()

    return success_response({"message": "Default method updated"})



@bp.route("/payment-methods", methods=["GET"])
@jwt_required()
def list_payment_methods():
    uid = get_jwt_identity()
    methods = PaymentMethod.query.filter_by(user_id=uid).all()

    return success_response([
        {
            "id": m.id,
            "method": m.method,
            "details": m.details,
            "is_default": m.is_default
        } for m in methods
    ])


@bp.route("/payment-methods/<pm_id>", methods=["PATCH"])
@jwt_required()
def update_payment_method(pm_id):
    data = request.get_json() or {}
    new_details = data.get("details")

    if not new_details:
        return error_response("VALIDATION_ERROR", "Details are required")

    uid = get_jwt_identity()

    pm = PaymentMethod.query.filter_by(id=pm_id, user_id=uid).first()
    if not pm:
        return error_response("NOT_FOUND", "Payment method not found", status=404)

    pm.details = new_details
    db.session.commit()

    return success_response({"message": "Payment method updated"})


@bp.route("/init", methods=["POST"])
@jwt_required()
def init_order_payment():
    uid = get_jwt_identity()
    data = request.get_json() or {}

    order_id = data.get("order_id")
    order = Order.query.get(order_id)

    if not order or order.client_id != uid:
        return error_response("FORBIDDEN", "Invalid order", 403)

    if order.payment_status == "paid":
        return error_response("ALREADY_PAID", "Order already paid", 400)

    amount_usd = order.client_budget

    reference = f"order_{order.id}_{uuid.uuid4().hex[:8]}"

    payment = OrderPayment(
        order_id=order.id,
        client_id=uid,
        reference=reference,
        amount_usd=amount_usd,
        status="pending"
    )

    db.session.add(payment)
    db.session.commit()

    return success_response({
        "public_key": current_app.config["PAYSTACK_PUBLIC_KEY"],
        "email": order.client.email,
        "amount": amount_usd,
        "currency": "USD",
        "reference": reference,
        "callback_url": current_app.config["PAYSTACK_CALLBACK_URL"],
        "metadata": {
            "order_id": order.id,
            "payment_id": payment.id,
            "client_id": uid,
            "usd_amount": amount_usd
        }
    })


@bp.route("", methods=["POST"])
def handle_paystack_webhook():
    secret = current_app.config["PAYSTACK_SECRET_KEY"]
    signature = request.headers.get("x-paystack-signature")

    body = request.get_data()

    computed = hmac.new(
        secret.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if not signature or computed != signature:
        return "Invalid signature", 401

    payload = request.json

    if payload.get("event") == "charge.success":
        data = payload["data"]
        reference = data["reference"]

        payment = OrderPayment.query.filter_by(reference=reference).first()
        if not payment:
            return "Payment not found", 404

        # Idempotency guard
        if payment.status == "success":
            return "OK", 200

        payment.status = "success"
        payment.paid_at = datetime.utcnow()

        order = Order.query.get(payment.order_id)
        if order:
            order.payment_status = "paid"

        db.session.commit()

    return "OK", 200
