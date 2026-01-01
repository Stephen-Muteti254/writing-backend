from app.extensions import db
from datetime import datetime
import uuid

def gen_submission_id():
    return f"sub-{str(uuid.uuid4())[:8]}"

class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.String(50), primary_key=True, default=gen_submission_id)
    order_id = db.Column(db.String(50), db.ForeignKey("orders.id"), nullable=False)
    submission_number = db.Column(db.Integer, nullable=False)

    writer_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)

    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")
    files = db.Column(db.JSON, nullable=False, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    order = db.relationship("Order", backref="submissions", lazy=True)
    writer = db.relationship("User", lazy=True)

    db.UniqueConstraint("order_id", "submission_number")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "writer_id": self.writer_id,
            "submission_number": self.submission_number,
            "message": self.message,
            "status": self.status,
            "files": self.files,  # each file now has "type" included
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None,
            "writer_name": self.writer.full_name if self.writer else None
        }
