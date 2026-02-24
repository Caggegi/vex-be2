from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class QuotationDettagli(BaseModel):
    tipo_spedizione: str = Field(
        ..., description="N = nazionale, E = estero, I = import"
    )
    cosa_spedire: str = Field(
        ..., description="D = documenti, M = merce/pacchi, P = pallets"
    )
    contenuto: str = Field(..., description="Descrizione del contenuto")
    accessori: Optional[Dict[str, Any]] = Field(
        None, description="Accessori opzionali (contrassegno, assicurazione, ecc.)"
    )


class Collo(BaseModel):
    peso: float = Field(..., description="Peso del collo in kg")
    larghezza: int = Field(..., description="Larghezza in cm")
    profondita: int = Field(..., description="Profondità in cm")
    altezza: int = Field(..., description="Altezza in cm")
    nr_colli: int = Field(1, description="Numero colli uguali")


class Indirizzo(BaseModel):
    cap: str = Field(..., description="CAP")
    localita: str = Field(..., description="Località")
    provincia: str = Field(..., description="Provincia (sigla)")
    nazione: str = Field(..., description="Nazione (sigla ISO, es. IT)")
    country: Optional[str] = Field(
        None, description="Obbligatorio solo su USA e CANADA"
    )


class IndirizzoOrder(Indirizzo):
    nominativo: str = Field(..., description="Nominativo del mittente/destinatario")
    indirizzo: str = Field(..., description="Via, piazza, ecc.")
    email: str = Field(..., description="Email per notifiche")
    telefono: Optional[str] = Field(None)
    cellulare: str = Field(..., description="Numero di cellulare richiesto")
    contatto: str = Field(..., description="Persona di contatto")
    codicefiscale: Optional[str] = Field(None)


class QuotationRequest(BaseModel):
    dettagli: QuotationDettagli
    colli: List[Collo]
    mittente: Indirizzo
    destinatario: Indirizzo


class OrderDettagli(QuotationDettagli):
    note_cliente: Optional[str] = Field(None)
    note_contenuto: str = Field(...)
    file_ldv: Optional[bool] = Field(False)
    vettore: str = Field(..., description="Codice vettore scelto dalla quotation")
    idcustomer: Optional[int] = Field(None)
    custom: Optional[str] = Field(None)


class RitiroDettagli(BaseModel):
    ritirodove: str = Field(..., description="M = mittente")
    disponibile_dal: str = Field(..., description="Data ritiro (YYYY-MM-DD)")
    disponibile_ora: str = Field(..., description="Ora disponibile (HH:MM)")
    ritiro_mattina_dalle: Optional[str] = Field(None)
    ritiro_mattina_alle: Optional[str] = Field(None)
    ritiro_pomeriggio_dalle: Optional[str] = Field(None)
    ritiro_pomeriggio_alle: Optional[str] = Field(None)


class Ritiro(BaseModel):
    prenotazione: str = Field(..., description="S o N")
    dettagli: Optional[RitiroDettagli] = Field(None)


class OrderRequest(BaseModel):
    codice_offerta: str = Field(
        ..., description="Codice dell'offerta dalla chiamata quotation"
    )
    dettagli: OrderDettagli
    colli: List[Collo]
    mittente: IndirizzoOrder
    destinatario: IndirizzoOrder
    ritiro: Ritiro


class OrderFastRequest(BaseModel):
    dettagli: OrderDettagli
    colli: List[Collo]
    mittente: IndirizzoOrder
    destinatario: IndirizzoOrder
    ritiro: Ritiro


class GetWaybillDettagli(BaseModel):
    order_id: int
    waybill_base64: Optional[str] = Field("N", description="Y o N")
    single_waybills: Optional[str] = Field("N", description="Y o N")


class GetWaybillRequest(BaseModel):
    details: GetWaybillDettagli


class GetOrderDettagli(BaseModel):
    codice_offerta: Optional[str] = Field(None)
    custom: Optional[str] = Field(None)


class GetOrderRequest(BaseModel):
    dettagli: GetOrderDettagli


class AddFundDettagli(BaseModel):
    idcustomer: int
    amount: float


class AddFundRequest(BaseModel):
    dettagli: AddFundDettagli


class BalanceDettagli(BaseModel):
    idcustomer: Optional[int] = Field(None)


class BalanceRequest(BaseModel):
    dettagli: Optional[BalanceDettagli] = Field(None)


class CheckCouponDettagli(BaseModel):
    idcustomer: int
    vettore: str
    peso_totale: float
    tipo_spedizione: str
    cosa_spedire: str
    provincia: str
    nazione: str
    coupon: str


class CheckCouponRequest(BaseModel):
    dettagli: CheckCouponDettagli
