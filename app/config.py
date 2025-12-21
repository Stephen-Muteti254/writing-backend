import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080, http://127.0.0.1:8080, https://id-preview--1ddf316e-9ab9-41ad-ab11-efb95ff33ef9.lovable.app")
    RATELIMIT_HEADERS_ENABLED = True

    ACCESS_EXPIRES = int(os.getenv("ACCESS_EXPIRES", 86400))
    REFRESH_EXPIRES = int(os.getenv("REFRESH_EXPIRES", 86400))
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    UPLOAD_FOLDER = os.path.join(basedir, "uploads/applications")
    ORDERS_FOLDER = os.path.join(basedir, "uploads/orders")
    SUBMISSIONS_FOLDER = os.path.join(basedir, "uploads/submissions")
    SUPPORT_UPLOADS_FOLDER = os.path.join(basedir, "uploads/support_chats")
    WRITER_PAYOUT_PERCENTAGE = 0.30
    PAYSTACK_SECRET_KEY = "sk_live_e3c9231206431254561a88cd7d12b50098fe21f6"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
