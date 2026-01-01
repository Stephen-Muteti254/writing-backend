from app.extensions import db
from datetime import datetime
import uuid

def gen_msg_id():
    return f"msg-{str(uuid.uuid4())[:8]}"

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.String(50), primary_key=True, default=gen_msg_id)
    chat_id = db.Column(db.String(50), db.ForeignKey("chats.id"))
    sender_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship("Chat", backref="messages", lazy=True)
    sender = db.relationship("User", backref="messages", lazy=True)
