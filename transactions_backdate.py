from datetime import datetime, timedelta, timezone

from app.main import create_app
from app.extensions import db
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

USERS = [
    "usr-9d550792-f417-4b3a-bb13-608e149f9e2e",
    "usr-17c5a8bf-3934-448d-8fe0-b914244a341d",
    "usr-ace1f125-7348-474d-b4de-e0cafb313d0a",
]

# make window datetimes UTC-aware
WINDOW_BEFORE_START = datetime(2025, 11, 1, 9, 0, 0, tzinfo=timezone.utc)
WINDOW_AFTER_END    = datetime(2026, 1, 7, 18, 0, 0, tzinfo=timezone.utc)

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def spread(start: datetime, end: datetime, n: int):
    """Evenly spread n timestamps between start and end."""
    if n <= 0:
        return []
    delta = (end - start) / n
    return [start + i * delta for i in range(n)]


def apply_dates(transactions, start, end, label):
    """Assign new created_at dates to a list of transactions."""
    dates = spread(start, end, len(transactions))
    for tx, new_date in zip(transactions, dates):
        print(f"{label:<8} {tx.id} | {tx.created_at} → {new_date}")
        tx.created_at = new_date


# -------------------------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------------------------

def backdate_existing_deposits():
    print("🚀 Starting backdate_existing_deposits")

    with db.session.begin():
        for user_id in USERS:
            print(f"\n👤 Processing user: {user_id}")

            wallet = (
                db.session.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .one_or_none()
            )

            if not wallet:
                print("⚠️  No wallet found — skipping")
                continue

            print(f"💼 Wallet ID: {wallet.id}")

            # -------------------------------------------------------------------
            # Fetch withdrawals
            # -------------------------------------------------------------------
            withdrawals = (
                db.session.query(WalletTransaction)
                .filter(
                    WalletTransaction.wallet_id == wallet.id,
                    WalletTransaction.type == "withdrawal",
                )
                .order_by(WalletTransaction.created_at)
                .all()
            )

            if len(withdrawals) < 2:
                print("⚠️  Less than 2 withdrawals — skipping user")
                continue

            w1, w2 = withdrawals[0], withdrawals[1]

            print(f"⬇️  Withdrawal 1: {w1.created_at}")
            print(f"⬇️  Withdrawal 2: {w2.created_at}")

            # -------------------------------------------------------------------
            # Fetch deposits
            # -------------------------------------------------------------------
            deposits = (
                db.session.query(WalletTransaction)
                .filter(
                    WalletTransaction.wallet_id == wallet.id,
                    WalletTransaction.type == "deposit",
                )
                .order_by(WalletTransaction.created_at)
                .all()
            )

            print(f"💰 Deposits found: {len(deposits)}")

            if not deposits:
                print("⚠️  No deposits — skipping user")
                continue

            # -------------------------------------------------------------------
            # Split deposits into before / between / after based on position
            # -------------------------------------------------------------------
            n = len(deposits)
            n_before = max(1, n // 3)      # at least 1 deposit before
            n_between = max(1, n // 3)     # at least 1 deposit between
            n_after = n - n_before - n_between

            before  = deposits[:n_before]
            between = deposits[n_before:n_before+n_between]
            after   = deposits[n_before+n_between:]

            print(
                f"📊 Segments → "
                f"before={len(before)}, "
                f"between={len(between)}, "
                f"after={len(after)}"
            )

            # -------------------------------------------------------------------
            # Define time windows (UTC-aware)
            # -------------------------------------------------------------------
            before_start  = WINDOW_BEFORE_START
            before_end    = w1.created_at - timedelta(hours=1)

            between_start = w1.created_at + timedelta(hours=1)
            between_end   = w2.created_at - timedelta(hours=1)

            after_start   = w2.created_at + timedelta(hours=1)
            after_end     = WINDOW_AFTER_END

            # -------------------------------------------------------------------
            # Apply new timestamps
            # -------------------------------------------------------------------
            apply_dates(before, before_start, before_end, "BEFORE")
            apply_dates(between, between_start, between_end, "BETWEEN")
            apply_dates(after, after_start, after_end, "AFTER")

    print("\n✅ Backdating completed and committed.")


# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        backdate_existing_deposits()
