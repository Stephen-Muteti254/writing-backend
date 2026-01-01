from app.extensions import ma

class BidSchema(ma.Schema):
    class Meta:
        fields = ("id", "order_id", "order_title", "bid_amount", "original_budget", "status", "message", "is_counter_offer", "submitted_at", "response_deadline")
