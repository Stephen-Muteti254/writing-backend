from app.extensions import db
from datetime import datetime
import uuid

def gen_payment_id():
    return f"PAY-{str(uuid.uuid4())[:10]}"

class OrderPayment(db.Model):
    __tablename__ = "order_payments"

    __table_args__ = (
        db.Index("idx_order_payments_order_id", "order_id"),
        db.Index("idx_order_payments_status", "status"),
    )

    id = db.Column(db.String(50), primary_key=True, default=gen_payment_id)
    order_id = db.Column(db.String(50), db.ForeignKey("orders.id"), nullable=False, index=True)
    client_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)

    gateway = db.Column(db.String(50), default="paystack")
    reference = db.Column(db.String(255), unique=True, nullable=False)

    amount_usd = db.Column(db.Float, nullable=False)

    currency = db.Column(db.String(10), default="USD")
    status = db.Column(db.String(30), default="pending")

    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", backref="payments")
