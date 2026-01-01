from app.extensions import ma

class OrderListSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "subject", "type", "pages", "deadline", "budget", "status", "client", "progress", "description", "created_at")

class OrderDetailSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "subject", "type", "pages", "deadline", "budget", "status", "client", "writer", "progress", "description", "requirements", "attachments", "created_at", "updated_at")
