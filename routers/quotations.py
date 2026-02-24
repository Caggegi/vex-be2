from fastapi import APIRouter, HTTPException, Body
from config import settings
import requests

router = APIRouter(prefix="/quotations", tags=["quotations"])

from schemas.easyparcel import (
    QuotationRequest,
    OrderRequest,
    OrderFastRequest,
    GetWaybillRequest,
    GetOrderRequest,
    AddFundRequest,
    BalanceRequest,
    CheckCouponRequest,
)


def call_easyparcel(action: str, payload: dict):
    url = f"{settings.API_ENDPOINT.rstrip('/')}/{action}/{settings.API_KEY}"
    # Ensure call attribute is present in payload
    if "call" not in payload:
        payload["call"] = action
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/quotation", summary="Ottieni un preventivo")
def get_quotation(request: QuotationRequest):
    """
    Ottiene il preventivo di costo relativo ad una spedizione secondo i parametri.
    Restituisce un array di quotazioni dai vari vettori disponibili con eventuali servizi opzionali.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("quotation", payload)


@router.post("/order", summary="Acquista spedizione")
def create_order(request: OrderRequest):
    """
    Concretizza l'ordine della spedizione secondo una quotation precedente (codice_offerta richiesto).
    Verifica il credito e genera la spedizione.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("order", payload)


@router.post("/order-fast", summary="Acquisto spedizione fast")
def create_order_fast(request: OrderFastRequest):
    """
    Crea un ordine di spedizione senza aver richiesto e indicato un codice_offerta da un preventivo.
    Selezionare esplicitamente il vettore nelle properties 'dettagli'.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("order-fast", payload)


@router.post("/getwaybill", summary="Recupera la LDV (Waybill)")
def get_waybill(request: GetWaybillRequest):
    """
    Recupera i dati o i base64 delle Lettere di Vettura usando il codice ordine (ID).
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("getwaybill", payload)


@router.post("/getorder", summary="Recupera dettagli ordine")
def get_order(request: GetOrderRequest):
    """
    Consulta lo status o info di un ordine usando il `codice_offerta` o un custom reference.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("getorder", payload)


@router.post("/addfund", summary="Aggiungi fondi a un cliente figlio")
def add_fund(request: AddFundRequest):
    """
    Gira credito master del capofila ad un idcustomer secondario.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("addfund", payload)


@router.post("/balance", summary="Informazioni credito residuo")
def get_balance(request: BalanceRequest = None):
    """
    Visualizza il credito residuo dell'account e di un eventuale cliente figlio.
    """
    payload = (
        request.model_dump(exclude_none=True) if request and request.dettagli else {}
    )
    return call_easyparcel("balance", payload)


@router.post("/checkcoupon", summary="Valida uno sconto/coupon")
def check_coupon(request: CheckCouponRequest):
    """
    Verifica la validità di uno sconto per specifici parametri di spedizione.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("checkcoupon", payload)


@router.post("/apikeyinfo", summary="Informazioni dell'API Key")
def get_apikey_info():
    """
    Mostra i dati di licenza, credito base, restrizioni e permessi dell'API Key corrente.
    """
    payload = {"call": "apikeyinfo"}
    return call_easyparcel("apikeyinfo", payload)
