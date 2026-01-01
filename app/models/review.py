from app.extensions import db
from sqlalchemy.sql import func
from datetime import datetime
import uuid

def gen_uuid(prefix="rev"):
    return f"{prefix}-{str(uuid.uuid4())[:8]}"

class Review(db.Model):
    __tablename__ = "reviews"

    __table_args__ = (
        db.Index("idx_reviews_reviewee_id", "reviewee_id"),
        db.Index("idx_reviews_reviewer_id", "reviewer_id"),
        db.Index("idx_reviews_created_at", "created_at"),
    )

    id = db.Column(
        db.String(50),
        primary_key=True,
        default=lambda: gen_uuid("rev")
    )

    order_id = db.Column(
        db.String(50),
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    reviewer_id = db.Column(
        db.String(50),
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    reviewee_id = db.Column(
        db.String(50),
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    review = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    order = db.relationship(
        "Order",
        backref=db.backref("review", uselist=False)
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewer_id]
    )

    reviewee = db.relationship(
        "User",
        foreign_keys=[reviewee_id]
    )
