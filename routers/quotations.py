from fastapi import APIRouter, HTTPException, Body, Depends
from auth.dependencies import get_current_user
from models.user import User, Person, Address
from models.shipment import Shipping
from config import settings
from utils.easyparcel import call_easyparcel
import requests
import re
import smtplib
from email.message import EmailMessage
import json

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




def parse_localita(localita_str: str, default_prov: str):
    """Estrae la località e la provincia se formattato come 'Località (PR)'"""
    match = re.match(r"^(.*?)\s*\(([a-zA-Z]{2})\)$", localita_str)
    if match:
        return match.group(1).strip(), match.group(2).upper()
    return localita_str, default_prov


@router.post("/quotation", summary="Ottieni un preventivo")
def get_quotation(request: QuotationRequest):
    """
    Ottiene il preventivo di costo relativo ad una spedizione secondo i parametri.
    Restituisce un array di quotazioni dai vari vettori disponibili con eventuali servizi opzionali.
    """
    payload = request.model_dump(exclude_none=True)
    return call_easyparcel("quotation", payload)


@router.post("/order-old", summary="Acquista spedizione")
def create_order(request: OrderRequest, current_user: User = Depends(get_current_user)):
    """
    Concretizza l'ordine della spedizione secondo una quotation precedente (codice_offerta richiesto).
    Verifica il credito e genera la spedizione.
    """
    if (
        settings.MY_PHONE == "brokenphonenumber"
        or request.mittente.cellulare != settings.MY_PHONE
    ):
        return {"result": "NO", "message": "Acquisto non consentito"}
    mitt_loc, mitt_prov = parse_localita(request.mittente.localita, request.mittente.provincia)
    dest_loc, dest_prov = parse_localita(request.destinatario.localita, request.destinatario.provincia)

    # Update the request model so the parsed values are included in payload
    request.mittente.localita = mitt_loc
    request.mittente.provincia = mitt_prov
    request.destinatario.localita = dest_loc
    request.destinatario.provincia = dest_prov

    payload = request.model_dump(exclude_none=True)

    # EasyParcel richiede che il "codice_offerta" stia anche nell'oggetto "dettagli"
    # sebbene la documentazione spesso lo riporti alla radice.
    if "codice_offerta" in payload and "dettagli" in payload:
        payload["dettagli"]["codice_offerta"] = payload["codice_offerta"]

    response = call_easyparcel("order", payload)

    if response and response.get("result") == "OK":
        # Split nominativo if possible
        mittente_names = request.mittente.nominativo.split(" ", 1)
        destinatario_names = request.destinatario.nominativo.split(" ", 1)

        sender_address = Address(
            country=request.mittente.nazione,
            zip=request.mittente.cap,
            city=request.mittente.localita,
            address=request.mittente.indirizzo,
            number=0,
        )
        receiver_address = Address(
            country=request.destinatario.nazione,
            zip=request.destinatario.cap,
            city=request.destinatario.localita,
            provincia=request.destinatario.provincia,
            address=request.destinatario.indirizzo,
            number=0,
        )

        sender = Person(
            name=mittente_names[0],
            surname=mittente_names[1] if len(mittente_names) > 1 else "",
            address=[sender_address],
        )
        receiver = Person(
            name=destinatario_names[0],
            surname=destinatario_names[1] if len(destinatario_names) > 1 else "",
            email=request.destinatario.email,
            phone=request.destinatario.cellulare,
            address=[receiver_address],
        )

        shipment = Shipping(
            sender=sender,
            receiver=receiver,
            company={
                "vettore": request.dettagli.vettore,
                "lettera_vettura": response.get("lettera_vettura", ""),
            },
            price=float(response.get("importo_scalato", 0.0)),
            status="in_progress",
            raw_response=response,
        )
        shipment.save()

        if not current_user.history:
            from models.user import History

            current_user.history = History()

        current_user.history.shippings.append(shipment)
        
        # Salva il destinatario nella clients_list se non presente
        if receiver not in (current_user.clients_list or []):
            if current_user.clients_list is None:
                current_user.clients_list = []
            current_user.clients_list.append(receiver)

        current_user.save()

        # Send email with formatted raw response
        try:
            msg = EmailMessage()
            msg["Subject"] = "Conferma Ordine Spedizione EasyParcel"
            msg["From"] = settings.SMTP_USER
            msg["To"] = current_user.email
            
            formatted_response = json.dumps(response, indent=4, ensure_ascii=False)
            
            content = f"""Gentile utente,
            
Ti confermiamo la ricezione del tuo ordine di spedizione.
Di seguito i dettagli completi restituiti dal sistema:

{formatted_response}

Grazie per aver scelto il nostro servizio.
"""
            msg.set_content(content)

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending order confirmation email: {e}")

    return response


@router.post("/order", summary="Acquisto spedizione fast")
def create_order_fast(
    request: OrderFastRequest, current_user: User = Depends(get_current_user)
):
    """
    Crea un ordine di spedizione senza aver richiesto e indicato un codice_offerta da un preventivo.
    Selezionare esplicitamente il vettore nelle properties 'dettagli'.
    """

    """
    Una risposta sarebbe:
    {
    "result": "OK",
    "errorcode": "0",
    "errormessage": "ACQUISTO OK",
    "codice_offerta": "CROM_69b71bf09f240",
    "custom": "",
    "ordine": "EAS-CROM_69b71bf09f240",
    "id_ordine": 23835140,
    "importo": "5.37",
    "timestamp": "2026-03-15 20:52:01",
    "version": "1.1.20",
    "lettera_vettura": "3C1906J020905",
    "url_ldv": "https://api.easyparcel.it/ldv/23835140_69b71bf200007.pdf",
    "codice_ritiro": "Service not required",
    "url_bordero": "https://api.easyparcel.it/tmp/35228_bordero_20260315215204.pdf",
    "ldv_base64": "JVBERi0xLj...",
    "single_waybills": [
        {
            "waybill_number": "3C1906J020905",
            "waybill_base64": "JVB..."
        }]
    }
    """
    if (
        settings.MY_PHONE == "brokenphonenumber"
        or request.mittente.cellulare != settings.MY_PHONE
    ):
        return {"result": "NO", "message": "Acquisto non consentito"}
    mitt_loc, mitt_prov = parse_localita(request.mittente.localita, request.mittente.provincia)
    dest_loc, dest_prov = parse_localita(request.destinatario.localita, request.destinatario.provincia)

    # Update the request model so the parsed values are included in payload
    request.mittente.localita = mitt_loc
    request.mittente.provincia = mitt_prov
    request.destinatario.localita = dest_loc
    request.destinatario.provincia = dest_prov

    payload = request.model_dump(exclude_none=True)
    response = call_easyparcel("order-fast", payload)

    if response and response.get("result") == "OK":
        # Split nominativo if possible
        mittente_names = request.mittente.nominativo.split(" ", 1)
        destinatario_names = request.destinatario.nominativo.split(" ", 1)

        sender_address = Address(
            country=request.mittente.nazione,
            zip=request.mittente.cap,
            city=request.mittente.localita,
            address=request.mittente.indirizzo,
            number=0,
        )
        receiver_address = Address(
            country=request.destinatario.nazione,
            zip=request.destinatario.cap,
            city=request.destinatario.localita,
            provincia=request.destinatario.provincia,
            address=request.destinatario.indirizzo,
            number=0,
        )

        sender = Person(
            name=mittente_names[0],
            surname=mittente_names[1] if len(mittente_names) > 1 else "",
            address=[sender_address],
        )
        receiver = Person(
            name=destinatario_names[0],
            surname=destinatario_names[1] if len(destinatario_names) > 1 else "",
            email=request.destinatario.email,
            phone=request.destinatario.cellulare,
            address=[receiver_address],
        )

        shipment = Shipping(
            sender=sender,
            receiver=receiver,
            company={
                "vettore": request.dettagli.vettore,
                "lettera_vettura": response.get("lettera_vettura", ""),
            },
            price=float(response.get("importo_scalato", 0.0)),
            status="in_progress",
            raw_response=response,
        )
        shipment.save()

        if not current_user.history:
            from models.user import History

            current_user.history = History()

        current_user.history.shippings.append(shipment)
        
        # Salva il destinatario nella clients_list se non presente
        if receiver not in (current_user.clients_list or []):
            if current_user.clients_list is None:
                current_user.clients_list = []
            current_user.clients_list.append(receiver)

        current_user.save()

        # Send email with formatted raw response
        try:
            msg = EmailMessage()
            msg["Subject"] = "Conferma Ordine Spedizione EasyParcel"
            msg["From"] = settings.SMTP_USER
            msg["To"] = current_user.email
            
            formatted_response = json.dumps(response, indent=4, ensure_ascii=False)
            
            content = f"""Gentile utente,
            
Ti confermiamo la ricezione del tuo ordine di spedizione.
Di seguito i dettagli completi restituiti dal sistema:

{formatted_response}

Grazie per aver scelto il nostro servizio.
"""
            msg.set_content(content)

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending order confirmation email: {e}")

    return response


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
