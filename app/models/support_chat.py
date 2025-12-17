from app.extensions import db
from datetime import datetime
import uuid

def gen_support_chat_id():
    return f"schat-{str(uuid.uuid4())[:8]}"

class SupportChat(db.Model):
    __tablename__ = "support_chats"

    id = db.Column(db.String(50), primary_key=True, default=gen_support_chat_id)

    # Owner of the support chat (writer OR client)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Warning system (same as normal chat)
    warning_risk = db.Column(db.String(20))
    warning_message = db.Column(db.Text)
    warning_expires_at = db.Column(db.DateTime)
    warning_active = db.Column(db.Boolean, default=False)
    warning_for_user_id = db.Column(db.String(50))

    user = db.relationship("User", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", name="uq_support_chat_user"),
    )
