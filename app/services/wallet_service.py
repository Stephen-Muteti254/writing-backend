from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.withdrawal_request import WithdrawalRequest
from app.utils.ids import gen_uuid
from datetime import datetime

def get_wallet_balance(user_id):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return {
            "available_balance": 0.0,
            "currency": "USD"
        }

    return {
        "available_balance": float(wallet.balance),
        "currency": wallet.currency
    }
