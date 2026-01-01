from app.extensions import db
from datetime import datetime, timedelta
import uuid

def gen_bid_id():
    return f"BID-{str(uuid.uuid4())[:8]}"

class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.String(50), primary_key=True, default=gen_bid_id)
    order_id = db.Column(db.String(50), db.ForeignKey("orders.id"), nullable=False, index=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False, index=True)

    # What writer entered (30% world)
    writer_amount = db.Column(db.Float, nullable=False)

    # What client sees / pays (100% world)
    client_amount = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(50), default="open")
    message = db.Column(db.Text, nullable=True)
    is_counter_offer = db.Column(db.Boolean, default=False)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order = db.relationship("Order", backref=db.backref("bids", lazy=True, cascade="all, delete-orphan"))
    user = db.relationship("User", backref=db.backref("bids", lazy=True))

    def get_derived_status(self) -> str:
        """
        Compute the effective status for the bid, including unconfirmed bids.
        """
        if self.status in ["accepted", "rejected", "cancelled"]:
            return self.status
        if self.order and self.order.updated_at and self.order.updated_at > self.submitted_at:
            return "unconfirmed"
        return self.status

    def serialize(self, include_user_info=False, viewer_role=None):
        if viewer_role not in ("writer", "client", "admin"):
            raise ValueError("viewer_role is required to serialize bid amount correctly")

        data = {
            "id": self.id,
            "order_id": self.order_id,
            "status": self.get_derived_status(),
            "message": self.message,
            "submitted_at": self.submitted_at.isoformat() + "Z",
        }

        if viewer_role == "writer":
            data["amount"] = self.writer_amount
        else:
            data["amount"] = self.client_amount

        if include_user_info and self.user:
            data.update({
                "writerId": self.user.id,
                "writerName": self.user.full_name,
                "writerRating": getattr(self.user, "rating", 0),
            })

        return data

