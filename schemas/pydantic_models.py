from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# --- Address ---
class AddressModel(BaseModel):
    country: str = Field(..., description="Country name")
    zip: str = Field(..., description="ZIP code")
    city: str = Field(..., description="City name")
    address: str = Field(..., description="Street address")
    number: int = Field(..., description="Street number")


# --- Person ---
class PersonModel(BaseModel):
    name: str = Field(..., description="First name")
    surname: str = Field(..., description="Last name")
    address: List[AddressModel] = Field(default_factory=list)


class OperationModel(BaseModel):
    tx_id: Optional[str] = Field(None, alias="id")
    date: datetime = Field(default_factory=datetime.utcnow)
    title: Optional[str] = None
    description: Optional[str] = None
    subDescription: Optional[str] = None
    amount: float = Field(..., description="Operation amount")
    tx_type: str = Field("online", alias="type")

    class Config:
        populate_by_name = True


# --- Shipping ---
class ShippingModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    sender: PersonModel
    receiver: PersonModel
    company: Dict[str, Any] = Field(..., description="Shipping company details")
    price: float = Field(..., description="Shipping price")
    status: str = Field(..., description="Status: shipped, delivered, canceled, etc.")

    class Config:
        populate_by_name = True


# --- History ---
class HistoryModel(BaseModel):
    shippings: List[ShippingModel] = Field(default_factory=list)
    credits: List[OperationModel] = Field(default_factory=list)


# --- User ---
class UserModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    password: str
    info: PersonModel
    type: str = Field(..., description="admin | user")
    credit: float = Field(0.0, description="User credit balance")
    history: HistoryModel = Field(default_factory=HistoryModel)
    clients: PersonModel  # Based on image, it's a single Person object. If it should be multiple, it would be List[PersonModel].

    class Config:
        populate_by_name = True


# --- API Specific Models (Keep for registration/login compatibility if needed) ---


class UserRegisterModel(BaseModel):
    email: EmailStr
    password: str
    info: PersonModel
    type: str = "user"


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str


class UserUpdateModel(BaseModel):
    info: Optional[PersonModel] = None
    credit: Optional[float] = None
    type: Optional[str] = None


class ShipmentCreateModel(BaseModel):
    sender: PersonModel
    receiver: PersonModel
    company: Dict[str, Any]
    price: float
    status: str = "pending"


class ShipmentUpdateModel(BaseModel):
    sender: Optional[PersonModel] = None
    receiver: Optional[PersonModel] = None
    company: Optional[Dict[str, Any]] = None
    price: Optional[float] = None
    status: Optional[str] = None
