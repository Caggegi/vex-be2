import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    MONGO_DB_NAME = "VexONE"
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/VexONE")
    API_KEY = os.getenv(
        "EASYPARCEL_KEY",
        "brokenapikey",
    )
    API_ENDPOINT = os.getenv("EASYPARCEL_ENDPOINT", "https://broken.api.easyparcel.it/")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    MY_PHONE = os.getenv("MY_PHONE", "brokenphonenumber")


settings = Settings()
