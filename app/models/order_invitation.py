from app.extensions import db
from datetime import datetime
import uuid

class OrderInvitation(db.Model):
    __tablename__ = "order_invitations"
    id = db.Column(db.String(50), primary_key=True, default=lambda: f"INV-{uuid.uuid4().hex[:8]}")
    order_id = db.Column(db.String(50), db.ForeignKey("orders.id"), nullable=False)
    writer_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", backref=db.backref("invitations", lazy=True, cascade="all, delete-orphan"))
    writer = db.relationship("User", backref=db.backref("invitations_received", lazy=True))
