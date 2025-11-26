from mongoengine import connect
from config import settings

def connect_db():
    connect(host=settings.MONGO_URL)

def disconnect_db():
    from mongoengine import disconnect
    disconnect()
