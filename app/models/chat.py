from app.extensions import db
from datetime import datetime
import uuid

def gen_chat_id():
    return f"chat-{str(uuid.uuid4())[:8]}"

class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(db.String(50), primary_key=True, default=gen_chat_id)

    # Link chat to an order (nullable=False if all chats must be order-based)
    order_id = db.Column(db.String(50), db.ForeignKey("orders.id"), nullable=False)

    # Two participants explicitly: client and writer
    client_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    writer_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    client = db.relationship("User", foreign_keys=[client_id], lazy=True)
    writer = db.relationship("User", foreign_keys=[writer_id], lazy=True)
    order = db.relationship("Order", backref="chats", lazy=True)

    warning_risk = db.Column(db.String(20), nullable=True)
    warning_message = db.Column(db.Text, nullable=True)
    warning_expires_at = db.Column(db.DateTime, nullable=True)
    warning_active = db.Column(db.Boolean, default=False)
    warning_for_user_id = db.Column(db.String(50), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("order_id", "client_id", "writer_id", name="uq_chat_order_client_writer"),
    )
