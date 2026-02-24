from fastapi import APIRouter
from config import settings
import requests

router = APIRouter(
    prefix="/api_info",
    tags=["api_info"]
)


'''
{
	"response":{
		"azienda":string(company),
		"logo":string(url logo),
		"system":string("API"),
		"call":string("apikeyinfo"),
		"dettagli":{
			"apikey":string,
			"cliente":string,
			"attivazione":string("2026-01-01"),
			"scadenza":string("2026-12-31"),
			"ip_access":string("Unlimited"),
			"limite_giornaliero":string("Unlimited"),
			"fast_quote":string("false"),
			"credito_prepagato":float(125.00),
			"live":string("true"),
			"email_ordine_mittente":string("true"),
			"ldv_api":string("")
		},
		"timestamp":string("2026-01-03 14:50:19"),
		"version":string("1.1.20")
	}
}
'''
@router.get("/")
def get_api_info():
    response = requests.post(settings.API_ENDPOINT+"/apikeyinfo/"+settings.API_KEY)
    if response.ok:
        return response.content.json()
    return None