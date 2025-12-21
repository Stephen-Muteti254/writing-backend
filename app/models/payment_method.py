from app.extensions import db
from datetime import datetime
import uuid

def gen_method_id():
    return f"pm-{str(uuid.uuid4())[:8]}"

class PaymentMethod(db.Model):
    __tablename__ = "payment_methods"

    id = db.Column(db.String(50), primary_key=True, default=gen_method_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    method = db.Column(db.String(50))
    details = db.Column(db.String(255))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="payment_methods", lazy=True)
