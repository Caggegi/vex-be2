import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    MONGO_DB_NAME = "VexONE"
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27018/VexONE")

settings = Settings()
