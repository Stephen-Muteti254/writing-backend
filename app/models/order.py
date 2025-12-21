from app.extensions import db
from datetime import datetime
import uuid

def gen_order_id():
    return f"ORD-{str(uuid.uuid4())[:8]}"

class Order(db.Model):
    __tablename__ = "orders"

    __table_args__ = (
        db.Index("idx_orders_payment_status", "payment_status"),
    )

    id = db.Column(db.String(50), primary_key=True, default=gen_order_id)

    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    type = db.Column(db.String(100))
    pages = db.Column(db.Integer, default=1)
    deadline = db.Column(db.DateTime)

    client_budget = db.Column(db.Numeric(10, 2), nullable=False)
    writer_budget = db.Column(db.Numeric(10, 2), nullable=False)

    minimum_allowed_budget = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(50), default="in_progress")

    client_id = db.Column(
        db.String(50),
        db.ForeignKey("users.id"),
        nullable=True
    )

    writer_id = db.Column(
        db.String(50),
        db.ForeignKey("users.id"),
        nullable=True
    )

    progress = db.Column(db.Integer, default=0)

    description = db.Column(db.Text)
    requirements = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    tags = db.Column(db.ARRAY(db.String), default=list)

    detailed_requirements = db.Column(db.Text)
    additional_notes = db.Column(db.Text)

    payment_status = db.Column(
        db.String(30),
        nullable=False,
        default="unpaid"
    )

    # Relationships
    client = db.relationship(
        "User",
        foreign_keys=[client_id],
        backref="client_orders",
        lazy=True
    )

    writer = db.relationship(
        "User",
        foreign_keys=[writer_id],
        backref="writer_orders",
        lazy=True
    )
