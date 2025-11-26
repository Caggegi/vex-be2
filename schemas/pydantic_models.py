from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Shared Models ---

class AddressModel(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    zip: str = Field(..., description="ZIP code")
    country: str = Field(..., description="Country code (e.g., IT)")

class UserProfileModel(BaseModel):
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: str = Field(..., description="Phone number")
    vat_number: Optional[str] = Field(None, description="VAT number if applicable")

# --- User Models ---

class UserRegisterModel(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    profile: UserProfileModel

class UserLoginModel(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")

class UserUpdateModel(BaseModel):
    profile: Optional[UserProfileModel] = None
    default_address: Optional[AddressModel] = None
    vat_address: Optional[AddressModel] = None

# --- Shipment Models ---

class ContactInfoModel(BaseModel):
    name: str = Field(..., description="Contact name")
    address: str = Field(..., description="Full address")
    contact: str = Field(..., description="Phone or email contact")

class DimensionsModel(BaseModel):
    l: float = Field(..., description="Length in cm")
    w: float = Field(..., description="Width in cm")
    h: float = Field(..., description="Height in cm")

class PackageDetailsModel(BaseModel):
    weight_kg: float = Field(..., description="Weight in kg")
    dimensions_cm: DimensionsModel
    content_type: str = Field(..., description="Type of content (e.g., electronics)")

class CostModel(BaseModel):
    amount: float = Field(..., description="Cost amount")
    currency: str = Field(..., description="Currency code (e.g., EUR)")

class TrackingEventModel(BaseModel):
    status: str = Field(..., description="Event status")
    timestamp: datetime = Field(..., description="Event timestamp")
    location: Optional[str] = Field(None, description="Event location")
    description: Optional[str] = Field(None, description="Event description")
    driver_id: Optional[str] = Field(None, description="Driver ID if applicable")

class ShipmentCreateModel(BaseModel):
    tracking_code: str = Field(..., description="Unique tracking code")
    status: str = Field(..., description="Current status")
    sender: ContactInfoModel
    recipient: ContactInfoModel
    package_details: PackageDetailsModel
    cost: CostModel
    tracking_history: Optional[List[TrackingEventModel]] = []
    estimated_delivery: Optional[datetime] = None

class ShipmentUpdateModel(BaseModel):
    tracking_code: Optional[str] = None
    status: Optional[str] = None
    sender: Optional[ContactInfoModel] = None
    recipient: Optional[ContactInfoModel] = None
    package_details: Optional[PackageDetailsModel] = None
    cost: Optional[CostModel] = None
    tracking_history: Optional[List[TrackingEventModel]] = None
    estimated_delivery: Optional[datetime] = None
