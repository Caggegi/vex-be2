from marshmallow import Schema, fields, validate
from .common import ObjectIdField


class AddressSchema(Schema):
    country = fields.String(required=True)
    zip = fields.String(required=True)
    city = fields.String(required=True)
    address = fields.String(required=True)
    number = fields.Integer(required=True)


class PersonSchema(Schema):
    name = fields.String(required=True)
    surname = fields.String(required=True)
    address = fields.List(fields.Nested(AddressSchema))


class OperationSchema(Schema):
    date = fields.DateTime(dump_only=True)
    amount = fields.Float(required=True)


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
