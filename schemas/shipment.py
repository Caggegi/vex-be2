from marshmallow import Schema, fields
from .common import ObjectIdField
from .user import PersonSchema

class ShippingSchema(Schema):
    id = ObjectIdField(dump_only=True, data_key="_id")
    sender = fields.Nested(PersonSchema, required=True)
    receiver = fields.Nested(PersonSchema, required=True)
    company = fields.Dict(required=True)
    price = fields.Float(required=True)
    status = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ShipmentSchema(ShippingSchema):
    # Keeping ShipmentSchema name for compatibility with routers if they use it
    pass
