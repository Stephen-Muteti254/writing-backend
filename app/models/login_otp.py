from app.extensions import db
from datetime import datetime, timedelta
import uuid

def gen_uuid(prefix=None):
    uid = str(uuid.uuid4())
    return f"{prefix}-{uid}" if prefix else uid


class LoginOTP(db.Model):
    __tablename__ = "login_otps"

    id = db.Column(
        db.String(50),
        primary_key=True,
        default=lambda: gen_uuid("otp")
    )

    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    otp_hash = db.Column(db.String(255), nullable=False)

    expires_at = db.Column(db.DateTime, nullable=False)

    attempts = db.Column(db.Integer, default=0)

    used = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = db.relationship(
        "User",
        backref=db.backref(
            "login_otps",
            lazy="dynamic",
            cascade="all, delete-orphan"
        )
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def mark_used(self):
        self.used = True