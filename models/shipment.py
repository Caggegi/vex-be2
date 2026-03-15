from mongoengine import Document, StringField, DateTimeField, EmbeddedDocumentField, FloatField, DictField
from datetime import datetime
from .user import Person

class Shipping(Document):
    meta = {'collection': 'shipments'}
    sender = EmbeddedDocumentField(Person, required=True)
    receiver = EmbeddedDocumentField(Person, required=True)
    company = DictField(required=True) # "Object" in the image
    price = FloatField(required=True)
    status = StringField(required=True, default="pending") # "shipped" | "delivered" | "canceled"
    raw_response = DictField(required=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
