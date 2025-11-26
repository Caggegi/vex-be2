from mongoengine import Document, StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, FloatField, ListField, ObjectIdField
from datetime import datetime

class ContactInfo(EmbeddedDocument):
    name = StringField(required=True)
    address = StringField(required=True)
    contact = StringField(required=True)

class Dimensions(EmbeddedDocument):
    l = FloatField(required=True)
    w = FloatField(required=True)
    h = FloatField(required=True)

class PackageDetails(EmbeddedDocument):
    weight_kg = FloatField(required=True)
    dimensions_cm = EmbeddedDocumentField(Dimensions)
    content_type = StringField(required=True)

class Cost(EmbeddedDocument):
    amount = FloatField(required=True)
    currency = StringField(required=True)

class TrackingEvent(EmbeddedDocument):
    status = StringField(required=True)
    timestamp = DateTimeField(required=True)
    location = StringField()
    description = StringField()
    driver_id = StringField() # Keeping as string for flexibility as per example "ObjectId('driver_01')" which looks like a string representation or actual ObjectId. I'll use String for now to be safe or ObjectIdField if it's a real ref. The example shows "ObjectId('driver_01')" which is not a standard hex ObjectId. I'll use String.

class Shipment(Document):
    meta = {'collection': 'shipments'}
    tracking_code = StringField(required=True)
    customer_id = ObjectIdField(required=True) # Reference to User but storing ID
    status = StringField(required=True)
    sender = EmbeddedDocumentField(ContactInfo)
    recipient = EmbeddedDocumentField(ContactInfo)
    package_details = EmbeddedDocumentField(PackageDetails)
    cost = EmbeddedDocumentField(Cost)
    tracking_history = ListField(EmbeddedDocumentField(TrackingEvent))
    estimated_delivery = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
