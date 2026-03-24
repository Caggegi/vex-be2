from marshmallow import Schema, fields, validate
from .common import ObjectIdField


class AddressSchema(Schema):
    country = fields.String(required=True)
    zip = fields.String(required=True)
    city = fields.String(required=True)
    provincia = fields.String()
    address = fields.String(required=True)
    number = fields.Integer(required=True)


class PersonSchema(Schema):
    name = fields.String(required=True)
    surname = fields.String(required=True)
    email = fields.String()
    phone = fields.String()
    tax_code = fields.String()
    address = fields.List(fields.Nested(AddressSchema))


class OperationSchema(Schema):
    tx_id = fields.String(data_key="id")
    date = fields.DateTime(dump_only=True)
    title = fields.String()
    description = fields.String()
    subDescription = fields.String()
    amount = fields.Float(required=True)
    tx_type = fields.String(data_key="type")


class HistorySchema(Schema):
    shippings = fields.List(
        fields.Raw()
    )  # Can be more specific if we want, but Raw/Reference handles ObjectIds
    credits = fields.List(fields.Nested(OperationSchema))


class UserSchema(Schema):
    id = ObjectIdField(dump_only=True, data_key="_id")
    email = fields.Email(required=True)
    password_hash = fields.String(load_only=True)
    info = fields.Nested(PersonSchema, required=True)
    type = fields.String(required=True)
    credit = fields.Float()
    history = fields.Nested(HistorySchema)
    clients = fields.Nested(PersonSchema)
    clients_list = fields.List(fields.Nested(PersonSchema))
    easyparcel_id = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    info = fields.Nested(PersonSchema, required=True)
    type = fields.String(load_default="user")


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserUpdateSchema(Schema):
    info = fields.Nested(PersonSchema)
    credit = fields.Float()
    type = fields.String()
