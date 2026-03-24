from fastapi import APIRouter, HTTPException, status, Depends
from marshmallow import ValidationError
from schemas.shipment import ShipmentSchema
from schemas.pydantic_models import ShipmentCreateModel, ShipmentUpdateModel
from models.shipment import Shipping
from models.user import History
from auth.dependencies import get_current_user
from models.user import User
from bson import ObjectId

router = APIRouter(
    prefix="/shipments",
    tags=["shipments"]
)


def _user_shipping_ids(user: User) -> list:
    """
    Estrae gli ObjectId delle spedizioni dalla history dell'utente.
    history.shippings è una ListField(ReferenceField("Shipping")):
    ogni elemento può essere un documento già dereferenziato oppure
    un DBRef/LazyReference — gestiamo entrambi i casi.
    """
    if not user.history or not user.history.shippings:
        return []
    ids = []
    for ref in user.history.shippings:
        try:
            ids.append(ref.id)   # documento già dereferenziato
        except AttributeError:
            ids.append(ref.pk)   # DBRef / LazyReference
    return ids


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shipment(payload: ShipmentCreateModel, current_user: User = Depends(get_current_user)):
    schema = ShipmentSchema()
    try:
        data = schema.load(payload.model_dump())
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    # Crea e salva il documento Shipping
    shipment = Shipping(**data)
    shipment.save()

    # Aggiungi il riferimento alla history dell'utente
    if not current_user.history:
        current_user.history = History()

    current_user.history.shippings.append(shipment)
    
    # Salva il destinatario nella clients_list se non presente
    recipient = shipment.receiver
    if recipient:
        # Verifica se il destinatario è già presente (confronto diretto oggetti EmbeddedDocument)
        if recipient not in (current_user.clients_list or []):
            if current_user.clients_list is None:
                current_user.clients_list = []
            current_user.clients_list.append(recipient)

    current_user.save()

    return schema.dump(shipment)


@router.get("/")
async def get_shipments(current_user: User = Depends(get_current_user)):
    """
    Restituisce solo le spedizioni dell'utente corrente,
    usando gli ID presenti in history.shippings come filtro.
    """
    ids = _user_shipping_ids(current_user)
    if not ids:
        return []

    shipments = Shipping.objects(id__in=ids).order_by("-created_at")
    schema = ShipmentSchema(many=True)
    return schema.dump(shipments)


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Verifica che la spedizione appartenga all'utente
    ids = _user_shipping_ids(current_user)
    oid = ObjectId(shipment_id)
    if oid not in ids:
        raise HTTPException(status_code=404, detail="Shipment not found in your history")

    shipment = Shipping.objects(id=oid).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    schema = ShipmentSchema()
    return schema.dump(shipment)


@router.put("/{shipment_id}")
async def update_shipment(shipment_id: str, payload: ShipmentUpdateModel, current_user: User = Depends(get_current_user)):
    if not ObjectId.is_valid(shipment_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    ids = _user_shipping_ids(current_user)
    oid = ObjectId(shipment_id)
    if oid not in ids:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipment = Shipping.objects(id=oid).first()
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

    ids = _user_shipping_ids(current_user)
    oid = ObjectId(shipment_id)
    if oid not in ids:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipment = Shipping.objects(id=oid).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Rimuovi il riferimento dalla history e cancella il documento
    current_user.history.shippings = [
        ref for ref in current_user.history.shippings
        if (getattr(ref, 'id', None) or getattr(ref, 'pk', None)) != oid
    ]
    current_user.save()
    shipment.delete()

    return None


