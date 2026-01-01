from app.extensions import db
from datetime import datetime

class DeclinedOrder(db.Model):
    __tablename__ = "declined_orders"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, db.ForeignKey("orders.id"), nullable=False)
    writer_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
