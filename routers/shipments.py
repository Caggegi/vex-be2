from fastapi import APIRouter, HTTPException, status, Depends
from marshmallow import ValidationError
from schemas.shipment import ShipmentSchema
from schemas.pydantic_models import ShipmentCreateModel, ShipmentUpdateModel
from models.shipment import Shipping
from auth.dependencies import get_current_user
from models.user import User
from bson import ObjectId

router = APIRouter(
    prefix="/shipments",
    tags=["shipments"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shipment(payload: ShipmentCreateModel, current_user: User = Depends(get_current_user)):
    schema = ShipmentSchema()
    try:
        data = schema.load(payload.model_dump())
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)
    
    # Create the shipment
    shipment = Shipping(**data)
    shipment.save()
    
    # Add to user history
    # current_user.history is an EmbeddedDocument History
    if not current_user.history:
        from models.user import History
        current_user.history = History()
    
    current_user.history.shippings.append(shipment)
    current_user.save()
    
    return schema.dump(shipment)

@router.get("/")
async def get_shipments(current_user: User = Depends(get_current_user)):
    # Return all shipments for the current user from their history
    shipments = current_user.history.shippings
    schema = ShipmentSchema(many=True)
    return schema.dump(shipments)

@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if the shipment is in the user's history
    shipment = next((s for s in current_user.history.shippings if str(s.id) == shipment_id), None)
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found in your history")
        
    schema = ShipmentSchema()
    return schema.dump(shipment)

@router.put("/{shipment_id}")
async def update_shipment(shipment_id: str, payload: ShipmentUpdateModel, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Find the shipment in user history
    shipment = next((s for s in current_user.history.shippings if str(s.id) == shipment_id), None)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    schema = ShipmentSchema()
    try:
        data = schema.load(payload.model_dump(exclude_unset=True), partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    shipment.modify(**data)
    shipment.reload()
    
    return schema.dump(shipment)

@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(shipment_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Find the shipment reference in user history
    shipment_ref = next((s for s in current_user.history.shippings if str(s.id) == shipment_id), None)
    if not shipment_ref:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    # Delete the document and remove from history
    shipment_ref.delete()
    current_user.history.shippings.remove(shipment_ref)
    current_user.save()
    
    return None
