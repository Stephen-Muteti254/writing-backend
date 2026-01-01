from app.extensions import db
from sqlalchemy.sql import func
from app.models.user import User

class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), unique=True, nullable=False)

    balance = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(10), default="USD")

    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    user = db.relationship("User", backref=db.backref("wallet", uselist=False))
