from marshmallow import Schema, fields
from .common import ObjectIdField

class ContactInfoSchema(Schema):
    name = fields.String(required=True)
    address = fields.String(required=True)
    contact = fields.String(required=True)

class DimensionsSchema(Schema):
    l = fields.Float(required=True)
    w = fields.Float(required=True)
    h = fields.Float(required=True)

class PackageDetailsSchema(Schema):
    weight_kg = fields.Float(required=True)
    dimensions_cm = fields.Nested(DimensionsSchema)
    content_type = fields.String(required=True)

class CostSchema(Schema):
    amount = fields.Float(required=True)
    currency = fields.String(required=True)

class TrackingEventSchema(Schema):
    status = fields.String(required=True)
    timestamp = fields.DateTime(required=True)
    location = fields.String()
    description = fields.String()
    driver_id = fields.String()

class ShipmentSchema(Schema):
    id = ObjectIdField(dump_only=True)
    tracking_code = fields.String(required=True)
    customer_id = ObjectIdField(required=True)
    status = fields.String(required=True)
    sender = fields.Nested(ContactInfoSchema)
    recipient = fields.Nested(ContactInfoSchema)
    package_details = fields.Nested(PackageDetailsSchema)
    cost = fields.Nested(CostSchema)
    tracking_history = fields.List(fields.Nested(TrackingEventSchema))
    estimated_delivery = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
