from decimal import Decimal
from app.extensions import db
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
import uuid
from sqlalchemy.exc import SQLAlchemyError

def gen_tx_id():
    return f"tx_{uuid.uuid4().hex[:12]}"


def get_or_create_wallet(user_id, currency="USD"):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        wallet = Wallet(
            id=f"wal_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            currency=currency,
            balance=Decimal("0.00")
        )
        db.session.add(wallet)
        db.session.flush()
    return wallet


def credit_wallet(user_id, amount, tx_type, description="", ref_type=None, ref_id=None):
    wallet = (
        Wallet.query
        .filter_by(user_id=user_id)
        .with_for_update()
        .first()
    ) or get_or_create_wallet(user_id)

    amount = Decimal(amount)

    tx = WalletTransaction(
        id=gen_tx_id(),
        wallet_id=wallet.id,
        amount=amount,
        type=tx_type,
        reference_type=ref_type,
        reference_id=ref_id,
        description=description
    )

    wallet.balance += amount

    db.session.add(tx)
    return tx


def debit_wallet(user_id, amount, tx_type, description="", ref_type=None, ref_id=None):
    wallet = (
        Wallet.query
        .filter_by(user_id=user_id)
        .with_for_update()
        .first()
    )

    amount = Decimal(amount)

    if not wallet or wallet.balance < amount:
        raise ValueError("INSUFFICIENT_FUNDS")

    tx = WalletTransaction(
        id=gen_tx_id(),
        wallet_id=wallet.id,
        amount=amount,
        type=tx_type,
        reference_type=ref_type,
        reference_id=ref_id,
        description=description
    )

    wallet.balance -= amount

    db.session.add(tx)
    return tx


def approve_withdrawal(withdrawal_id):
    wr = WithdrawalRequest.query.get(withdrawal_id)
    if wr.status != "pending":
        return

    debit_wallet(
        user_id=wr.user_id,
        amount=wr.amount,
        tx_type="withdrawal",
        description="Wallet withdrawal",
        ref_type="withdrawal",
        ref_id=wr.id
    )

    wr.status = "completed"
    wr.processed_at = datetime.utcnow()


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


def has_sufficient_balance(user_id, amount):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return False
    return wallet.balance >= Decimal(amount)


def safe_debit_wallet(
    user_id,
    amount,
    tx_type,
    description="",
    ref_type=None,
    ref_id=None
):
    try:
        tx = debit_wallet(
            user_id=user_id,
            amount=amount,
            tx_type=tx_type,
            description=description,
            ref_type=ref_type,
            ref_id=ref_id
        )
        return tx
    except ValueError:
        raise
    except SQLAlchemyError:
        db.session.rollback()
        raise
