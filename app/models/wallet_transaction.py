from app.extensions import db
from sqlalchemy.sql import func
from app.models.wallet import Wallet

class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"

    id = db.Column(db.String(50), primary_key=True)
    wallet_id = db.Column(db.String(50), db.ForeignKey("wallets.id"), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    status = db.Column(db.String(30), default="completed")

    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.String(50))

    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())

    wallet = db.relationship("Wallet", backref="transactions")
