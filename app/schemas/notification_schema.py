from app.extensions import ma

class NotificationSchema(ma.Schema):
    class Meta:
        fields = ("id", "type", "title", "message", "is_read", "created_at", "metadata")
