from app.extensions import ma

class ChatListSchema(ma.Schema):
    class Meta:
        fields = ("id", "order_id", "order_title", "participant", "last_message", "unread_count")

class MessageSchema(ma.Schema):
    class Meta:
        fields = ("id", "chat_id", "sender", "content", "sent_at", "is_read", "attachments")
