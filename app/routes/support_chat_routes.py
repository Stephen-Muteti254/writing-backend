from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from app.extensions import db
from app.models.support_chat import SupportChat
from app.models.support_message import SupportMessage
from app.models.user import User
from app.services.support_chat_service import (
    get_or_create_support_chat,
    add_support_message
)
from app.services.chat_behavior_analyzer import analyze_chat_behavior
from app.utils.response_formatter import success_response, error_response

bp = Blueprint("support_chat", __name__, url_prefix="/api/v1/support-chat")

@bp.route("", methods=["POST"])
@jwt_required()
def create_or_get():
    uid = get_jwt_identity()
    chat = get_or_create_support_chat(uid)

    print(f"[SupportChat] User {uid} chat_id={chat.id}")

    return success_response({
        "chat": {
            "id": chat.id,
            "user_id": chat.user_id,
            "created_at": chat.created_at.isoformat() + "Z"
        }
    })

@bp.route("/<chat_id>/messages", methods=["GET"])
@jwt_required()
def list_messages(chat_id):
    uid = get_jwt_identity()
    chat = SupportChat.query.get(chat_id)

    print(f"[SupportChat] list_messages called with chat_id={chat_id} for user {uid}")

    if not chat:
        print(f"[SupportChat] Chat not found: {chat_id}")
        return error_response("NOT_FOUND", "Chat not found", 404)

    messages = [{
        "id": m.id,
        "sender": {
            "id": m.sender.id,
            "name": m.sender.full_name,
            "avatar": m.sender.profile_image,
            "role": m.sender.role
        },
        "content": m.content,
        "sent_at": m.created_at.isoformat() + "Z",
        "is_read": m.is_read,
        "attachments": m.attachments or []
    } for m in chat.messages]

    return success_response({
        "messages": messages,
        "warning": (
            {
                "active": chat.warning_active,
                "risk": chat.warning_risk,
                "message": chat.warning_message,
                "expires_at": chat.warning_expires_at.isoformat() + "Z"
            }
            if chat.warning_active and chat.warning_for_user_id == uid
            else None
        )
    })


@bp.route("/<chat_id>/messages", methods=["POST"])
@jwt_required()
def post_message(chat_id):
    uid = get_jwt_identity()
    chat = SupportChat.query.get(chat_id)

    if not chat:
        return error_response("NOT_FOUND", "Chat not found", 404)

    files = []
    content = ""

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        content = request.form.get("content", "")
        files = request.files.getlist("files")
    else:
        data = request.get_json(silent=True) or {}
        content = data.get("content", "")

    if not content and not files:
        return error_response("VALIDATION_ERROR", "Message or file required", 422)

    msg = add_support_message(chat_id, uid, content)

    # ---------- Save files ----------
    saved_files = []
    for f in files:
        fname, _ = save_support_file(f, chat_id, msg.id)
        saved_files.append({
            "id": uuid.uuid4().hex,
            "filename": f.filename,
            "mime": f.mimetype,
            "url": f"/api/v1/support-chat/files/{chat_id}/{msg.id}/{fname}"
        })

    msg.attachments = saved_files
    db.session.commit()

    # ---------- Behavior analysis ----------
    history = (
        SupportMessage.query
        .filter_by(support_chat_id=chat_id)
        .order_by(SupportMessage.created_at.desc())
        .limit(25)
        .all()[::-1]
    )

    analysis = analyze_chat_behavior(history)
    warning = None

    if analysis["risk"] in ("medium", "high"):
        chat.warning_active = True
        chat.warning_risk = analysis["risk"]
        chat.warning_message = (
            "We detected attempts to share personal or contact information. "
            "Please keep communication within the platform."
        )
        chat.warning_expires_at = datetime.utcnow() + timedelta(days=7)
        chat.warning_for_user_id = uid
        db.session.commit()

        warning = {
            "risk": chat.warning_risk,
            "message": chat.warning_message,
            "expires_at": chat.warning_expires_at.isoformat() + "Z",
        }

    return success_response({
        "id": msg.id,
        "chat_id": msg.support_chat_id,
        "content": msg.content,
        "sent_at": msg.created_at.isoformat() + "Z",
        "is_read": msg.is_read,
        "attachments": msg.attachments,
        "sender": {
            "id": msg.sender.id,
            "name": msg.sender.full_name,
            "avatar": msg.sender.profile_image,
            "role": msg.sender.role
        },
        "warning": warning
    })


@bp.route("/files/<chat_id>/<message_id>/<filename>", methods=["GET"])
@jwt_required()
def get_support_file(chat_id, message_id, filename):
    uid = get_jwt_identity()
    chat = SupportChat.query.get_or_404(chat_id)

    # Only chat owner or admin
    if chat.user_id != uid:
        return error_response("FORBIDDEN", "Access denied", 403)

    root_dir = current_app.config["SUPPORT_UPLOADS_FOLDER"]
    file_path = os.path.join(root_dir, chat_id, message_id, filename)

    if not os.path.exists(file_path):
        return error_response("NOT_FOUND", "File not found", 404)

    return send_file(file_path, as_attachment=True)

