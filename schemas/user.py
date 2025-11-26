from marshmallow import Schema, fields, validate
from .common import ObjectIdField

class AddressSchema(Schema):
    street = fields.String(required=True)
    city = fields.String(required=True)
    zip = fields.String(required=True)
    country = fields.String(required=True)

class UserProfileSchema(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone = fields.String(required=True)
    vat_number = fields.String()

class UserSchema(Schema):
    id = ObjectIdField(dump_only=True)
    email = fields.Email(required=True)
    password_hash = fields.String(load_only=True) # Usually we don't expose this
    role = fields.String()
    profile = fields.Nested(UserProfileSchema)
    default_address = fields.Nested(AddressSchema)
    vat_address = fields.Nested(AddressSchema)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    profile = fields.Nested(UserProfileSchema, required=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UserUpdateSchema(Schema):
    profile = fields.Nested(UserProfileSchema)
    default_address = fields.Nested(AddressSchema)
    vat_address = fields.Nested(AddressSchema)
