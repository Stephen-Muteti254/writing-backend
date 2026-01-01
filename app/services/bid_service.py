from app.extensions import db
from app.models.bid import Bid
from app.models.order import Order
from datetime import datetime, timedelta
from app.utils.response_formatter import error_response

def place_bid(order_id, user_id, writer_amount, client_amount, message=None):
    order = Order.query.get(order_id)
    if not order:
        raise ValueError("Order not found")

    # Prevent duplicate active bids
    existing = Bid.query.filter_by(
        order_id=order_id,
        user_id=user_id,
        status="open"
    ).first()

    if existing:
        raise ValueError("You already have an active bid on this order")

    bid = Bid(
        order_id=order_id,
        user_id=user_id,
        writer_amount=writer_amount,
        client_amount=client_amount,
        message=message,
    )

    db.session.add(bid)
    db.session.commit()
    return bid
