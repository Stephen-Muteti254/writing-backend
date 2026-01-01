from app.extensions import ma

class UserPublicSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "full_name", "role", "profile_image", "rating", "completed_orders")

class UserProfileSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "full_name", "profile_image", "bio", "rating", "completed_orders", "total_earned", "success_rate", "specializations", "joined_at")
