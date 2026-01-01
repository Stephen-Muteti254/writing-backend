from app.extensions import db
from datetime import datetime
import uuid

def gen_notif_id():
    return f"notif-{str(uuid.uuid4())[:8]}"

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(50), primary_key=True, default=gen_notif_id)
    sender_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    # For direct messages (single recipient)
    user_email = db.Column(db.String(100), db.ForeignKey("users.email"), nullable=True)

    # Target classification
    target_type = db.Column(db.String(50), default="individual")  # 'individual', 'group', 'all'
    target_group = db.Column(db.String(50), nullable=True)        # 'writers', 'clients', or None

    # Content
    type = db.Column(db.String(50), default="info")
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_notifications", lazy=True)
    recipient = db.relationship("User", foreign_keys=[user_email], backref="notifications", lazy=True)
