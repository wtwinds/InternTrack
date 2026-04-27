import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "interntrack")