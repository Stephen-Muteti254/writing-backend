from app.extensions import db
from sqlalchemy.sql import func
from app.models.user import User

class WithdrawalRequest(db.Model):
    __tablename__ = "withdrawal_requests"

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(30), default="pending")
    method = db.Column(db.String(50))
    destination = db.Column(db.String(255))

    requested_at = db.Column(db.DateTime, server_default=func.now())
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.String(50))

    user = db.relationship("User", backref="withdrawals")
