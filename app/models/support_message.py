from app.extensions import db
from datetime import datetime
import uuid

def gen_support_msg_id():
    return f"smsg-{str(uuid.uuid4())[:8]}"

class SupportMessage(db.Model):
    __tablename__ = "support_messages"

    id = db.Column(db.String(50), primary_key=True, default=gen_support_msg_id)

    support_chat_id = db.Column(
        db.String(50),
        db.ForeignKey("support_chats.id"),
        nullable=False
    )

    sender_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)

    content = db.Column(db.Text)
    attachments = db.Column(db.JSON, default=list)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship("SupportChat", backref="messages", lazy=True)
    sender = db.relationship("User", lazy=True)
