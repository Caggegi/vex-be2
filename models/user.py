from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    ListField,
    IntField,
    ReferenceField,
)
from datetime import datetime


class Address(EmbeddedDocument):
    country = StringField(required=True)
    zip = StringField(required=True)
    city = StringField(required=True)
    provincia = StringField()
    address = StringField(required=True)
    number = IntField(required=True)


class Person(EmbeddedDocument):
    name = StringField(required=True)
    surname = StringField(required=True)
    email = StringField()
    phone = StringField()
    tax_code = StringField()  # Codice Fiscale
    address = ListField(EmbeddedDocumentField(Address))


class Operation(EmbeddedDocument):
    tx_id = StringField()
    date = DateTimeField(default=datetime.utcnow)
    title = StringField()
    description = StringField()
    subDescription = StringField()
    amount = FloatField(required=True)
    tx_type = StringField(default="online")


class History(EmbeddedDocument):
    # Notice: we use a string for Shipping to avoid circular import if Shipping is in another file
    # Or we can use ListField(ReferenceField('Shipping')) if they are separate collections.
    # The image shows Shipping[] inside History. In Mongo, this could be a list of embedded or list of references.
    # Given Shipping is a top-level box in the diagram, it's likely a separate collection (Document).
    shippings = ListField(ReferenceField("Shipping"))
    credits = ListField(EmbeddedDocumentField(Operation))


class User(Document):
    meta = {"collection": "users"}
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    info = EmbeddedDocumentField(Person, required=True)
    type = StringField(required=True, choices=["admin", "user"], default="user")
    credit = FloatField(default=0.0)
    history = EmbeddedDocumentField(History, default=lambda: History())
    clients = EmbeddedDocumentField(Person)  # Single object as per image arrow
    clients_list = ListField(EmbeddedDocumentField(Person))  # Saved recipients
    easyparcel_id = StringField()  # EasyParcel customer ID (id_dva)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
