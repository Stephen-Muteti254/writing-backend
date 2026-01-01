from app.extensions import ma

class TransactionSchema(ma.Schema):
    class Meta:
        fields = ("id", "type", "amount", "description", "status", "order_id", "created_at")
