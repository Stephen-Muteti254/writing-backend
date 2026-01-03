import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        f"{os.getenv('DATABASE_URL')}"
        f"?sslmode=verify-full"
        f"&sslrootcert={os.getenv('DB_SSLROOTCERT')}"
    )

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://academichubpro.com"
    )

    RATELIMIT_HEADERS_ENABLED = True

    ACCESS_EXPIRES = int(os.getenv("ACCESS_EXPIRES", 86400))
    REFRESH_EXPIRES = int(os.getenv("REFRESH_EXPIRES", 86400))
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    UPLOAD_FOLDER = os.path.join(basedir, "uploads/applications")
    ORDERS_FOLDER = os.path.join(basedir, "uploads/orders")
    SUBMISSIONS_FOLDER = os.path.join(basedir, "uploads/submissions")
    SUPPORT_UPLOADS_FOLDER = os.path.join(basedir, "uploads/support_chats")
    PROFILES_FOLDER = os.path.join(basedir, "uploads/profiles")

    WRITER_PAYOUT_PERCENTAGE = 0.30
    PAYSTACK_SECRET_KEY = "sk_live_e3c9231206431254561a88cd7d12b50098fe21f6"
    PAYSTACK_PUBLIC_KEY = "pk_live_9b05dd85fd1beb35e3feb8571ae5c8f5abbc39f8"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
