from fastapi import APIRouter, HTTPException, status, Depends, Body
from marshmallow import ValidationError
from schemas.shipment import ShipmentSchema
from schemas.pydantic_models import ShipmentCreateModel, ShipmentUpdateModel
from models.shipment import Shipment
from auth.dependencies import get_current_user
from models.user import User
from bson import ObjectId

router = APIRouter(
    prefix="/shipments",
    tags=["shipments"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shipment(payload: ShipmentCreateModel, current_user: User = Depends(get_current_user)):
    # We want to ensure the shipment is assigned to the current user
    # But the schema requires customer_id.
    # Let's inject it if missing or overwrite it to ensure correctness
    data_dict = payload.model_dump()
    data_dict['customer_id'] = str(current_user.id)
    
    schema = ShipmentSchema()
    try:
        data = schema.load(data_dict)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)
    
    shipment = Shipment(**data)
    shipment.save()
    
    return schema.dump(shipment)

@router.get("/")
async def get_shipments(current_user: User = Depends(get_current_user)):
    # Return all shipments for the current user
    # If we had roles, we could allow admins to see all
    shipments = Shipment.objects(customer_id=current_user.id)
    schema = ShipmentSchema(many=True)
    return schema.dump(shipments)

@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
        
    shipment = Shipment.objects(id=shipment_id, customer_id=current_user.id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    schema = ShipmentSchema()
    return schema.dump(shipment)

@router.put("/{shipment_id}")
async def update_shipment(shipment_id: str, payload: ShipmentUpdateModel, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    shipment = Shipment.objects(id=shipment_id, customer_id=current_user.id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    schema = ShipmentSchema()
    try:
        # Partial update? The user didn't specify, but usually PUT is full, PATCH is partial.
        # Marshmallow load(partial=True) allows missing fields.
        # Let's assume we want to validate the fields that are sent.
        # But for a full update, we might expect all fields.
        # Let's go with partial=True to be flexible for now, or strict if we want to enforce structure.
        # Given the complexity of nested fields, partial updates are safer for a demo.
        data = schema.load(payload.model_dump(exclude_unset=True), partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    shipment.modify(**data)
    # Reload to get updated state
    shipment.reload()
    
    return schema.dump(shipment)

@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(shipment_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    shipment = Shipment.objects(id=shipment_id, customer_id=current_user.id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    shipment.delete()
    return None
