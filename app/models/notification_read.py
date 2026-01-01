from app.extensions import db
from datetime import datetime

class NotificationRead(db.Model):
    __tablename__ = "notification_reads"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False, unique=True)
    last_read = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("notification_read", uselist=False))
