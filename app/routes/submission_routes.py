import os
from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    current_app
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from app.extensions import db
from app.models.order import Order
from app.models.submission import Submission
from app.models.user import User
from app.services.submission_service import (
    create_submission,
    list_submissions,
    request_revision
)
from app.services.order_service import update_order_status
from app.utils.response_formatter import (
    success_response,
    error_response
)

bp = Blueprint(
    "submissions",
    __name__,
    url_prefix="/api/v1/orders"
)

def credit_writer_for_completed_order(order: Order):
    wallet = Wallet.query.filter_by(user_id=order.writer_id).first()
    if not wallet:
        wallet = Wallet(id=gen_uuid("wal"), user_id=order.writer_id)
        db.session.add(wallet)

    amount = order.writer_budget

    # Ledger entry
    tx = WalletTransaction(
        id=gen_uuid("txn"),
        wallet_id=wallet.id,
        amount=amount,
        type="order_earning",
        reference_type="order",
        reference_id=order.id,
        description=f"Earnings from order {order.id}"
    )

    wallet.balance += amount

    db.session.add(tx)


# ------------------------------------------------------------
# Writer submits work
# ------------------------------------------------------------
@bp.route("/<order_id>/submissions", methods=["POST"])
@jwt_required()
def submit_work(order_id):
    uid = get_jwt_identity()
    user = User.query.get(uid)

    if not user or user.role != "writer":
        return error_response("FORBIDDEN", "Writer access required", status=403)

    order = Order.query.get_or_404(order_id)

    # Writer must be assigned
    if order.writer_id != user.id:
        return error_response("FORBIDDEN", "You are not assigned to this order", status=403)

    files = request.files.getlist("files")
    message = request.form.get("message")

    if not files:
        return error_response("VALIDATION_ERROR", "At least one file is required", status=422)

    try:
        submission = create_submission(
            order=order,
            writer=user,
            files=files,
            message=message
        )

        update_order_status(order, status="submitted_for_review")

        return success_response(submission.to_dict(), status=201)

    except Exception as e:
        db.session.rollback()
        return error_response("SUBMISSION_ERROR", str(e), status=400)

# ------------------------------------------------------------
# Client views submissions
# ------------------------------------------------------------
@bp.route("/<order_id>/submissions", methods=["GET"])
@jwt_required()
def get_submissions(order_id):
    uid = get_jwt_identity()
    user = User.query.get(uid)

    order = Order.query.get_or_404(order_id)

    if user.role == "client" and order.client_id != user.id:
        return error_response("FORBIDDEN", "Not your order", status=403)

    submissions = list_submissions(order)
    payload = {
        "order_status": order.status,  # NEW: Include order status
        "writer_assigned": bool(order.writer_id),
        "submissions": [s.to_dict() for s in submissions]
    }
    return success_response(payload)

# ------------------------------------------------------------
# Client requests revision
# ------------------------------------------------------------
@bp.route(
    "/<order_id>/submissions/<submission_id>/revision",
    methods=["POST"]
)
@jwt_required()
def revision_request_endpoint(order_id, submission_id):
    uid = get_jwt_identity()
    user = User.query.get(uid)

    order = Order.query.get_or_404(order_id)

    if user.role != "client" or order.client_id != user.id:
        return error_response("FORBIDDEN", "Client access required", status=403)

    submission = Submission.query.filter_by(
        id=submission_id,
        order_id=order.id
    ).first_or_404()

    data = request.get_json() or {}
    message = data.get("message")

    if not message:
        return error_response("VALIDATION_ERROR", "Revision message required", status=422)

    request_revision(submission, message)
    update_order_status(order, status="revision_requested")

    return success_response({"message": "Revision requested"})


from flask import send_file

# ------------------------------------------------------------
# GET /orders/submissions/files/<order_id>/<submission_id>/<filename> — Download/preview submission file
# ------------------------------------------------------------
@bp.route("/submissions/files/<order_id>/<submission_id>/<filename>", methods=["GET"])
@jwt_required()
def get_submission_file(order_id, submission_id, filename):
    uid = get_jwt_identity()
    user = User.query.get(uid)

    # Ensure order exists
    order = Order.query.get_or_404(order_id)

    # Ensure user has access
    if user.role == "client" and order.client_id != user.id:
        return error_response("FORBIDDEN", "Not your order", status=403)
    if user.role == "writer" and order.writer_id != user.id:
        return error_response("FORBIDDEN", "Writer access required", status=403)

    # Ensure submission exists
    submission = Submission.query.filter_by(id=submission_id, order_id=order.id).first_or_404()

    # Ensure the file exists in submission record
    file_record = next((f for f in submission.files if f["name"] == filename), None)
    if not file_record:
        return error_response("NOT_FOUND", "File not found in submission", status=404)

    # Construct full path
    root_dir = current_app.config.get("SUBMISSIONS_FOLDER", "uploads/submissions")
    file_path = os.path.join(root_dir, order.id, submission.id, filename)

    if not os.path.exists(file_path):
        return error_response("NOT_FOUND", "File does not exist on server", status=404)

    return send_file(file_path, as_attachment=True)


# ------------------------------------------------------------
# Client marks order as complete
# ------------------------------------------------------------
@bp.route("/<order_id>/complete", methods=["POST"])
@jwt_required()
def complete_order(order_id):
    uid = get_jwt_identity()
    user = User.query.get(uid)

    order = Order.query.get_or_404(order_id)

    if order.status == "completed":
        return error_response(
            "ALREADY_COMPLETED",
            "Order already completed",
            400
        )

    # Only the client who owns the order can mark it complete
    if user.role != "client" or order.client_id != user.id:
        return error_response("FORBIDDEN", "Client access required", status=403)

    # Mark the order as complete
    update_order_status(order, status="completed")

    # credit the writer account
    credit_writer_for_completed_order(order)

    # Return harmonized success response
    return success_response(message=f"Order {order.id} marked as complete")
