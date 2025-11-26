from mongoengine import Document, StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField
from datetime import datetime

class Address(EmbeddedDocument):
    street = StringField(required=True)
    city = StringField(required=True)
    zip = StringField(required=True)
    country = StringField(required=True)

class UserProfile(EmbeddedDocument):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    phone = StringField(required=True)
    vat_number = StringField()

class User(Document):
    meta = {'collection': 'users'}
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    role = StringField(default="customer")
    profile = EmbeddedDocumentField(UserProfile)
    default_address = EmbeddedDocumentField(Address)
    vat_address = EmbeddedDocumentField(Address)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
