from app.main import create_app

from datetime import datetime
from app.extensions import db
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction

WINDOW_A_START = datetime(2025, 11, 1, 9, 0, 0)
WINDOW_A_END   = datetime(2025, 12, 15, 18, 0, 0)

WINDOW_B_START = datetime(2025, 12, 30, 9, 0, 0)
WINDOW_B_END   = datetime(2026, 1, 10, 18, 0, 0)

USERS = [
    "usr-9d550792-f417-4b3a-bb13-608e149f9e2e",
    "usr-17c5a8bf-3934-448d-8fe0-b914244a341d",
    "usr-ace1f125-7348-474d-b4de-e0cafb313d0a",
]

def spread(start, end, n):
    if n == 0:
        return []
    delta = (end - start) / n
    return [start + i * delta for i in range(n)]

def backdate_existing_deposits():
    print("Starting backdate_existing_deposits")

    with db.session.begin():
        for user_id in USERS:
            print(f"\n👤 Processing user: {user_id}")

            wallet = (
                db.session.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .one_or_none()
            )

            if not wallet:
                print("No wallet found")
                continue

            print(f"Wallet ID: {wallet.id}")

            deposits = (
                db.session.query(WalletTransaction)
                .filter(
                    WalletTransaction.wallet_id == wallet.id,
                    WalletTransaction.type == "deposit",
                )
                .order_by(WalletTransaction.created_at)
                .all()
            )

            print(f"Deposits found: {len(deposits)}")

            if not deposits:
                print("No deposit transactions — skipping user")
                continue

            split = int(len(deposits) * 0.7)

            pre = deposits[:split]
            post = deposits[split:]

            pre_dates = spread(WINDOW_A_START, WINDOW_A_END, len(pre))
            post_dates = spread(WINDOW_B_START, WINDOW_B_END, len(post))

            for tx, new_date in zip(pre, pre_dates):
                print(
                    f"PRE  {tx.id} | {tx.created_at} → {new_date}"
                )
                tx.created_at = new_date

            for tx, new_date in zip(post, post_dates):
                print(
                    f"POST {tx.id} | {tx.created_at} → {new_date}"
                )
                tx.created_at = new_date

    print("\n Backdating completed and committed.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        backdate_existing_deposits()
