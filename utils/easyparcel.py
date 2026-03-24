import requests
from fastapi import HTTPException
from config import settings

def call_easyparcel(action: str, payload: dict):
    url = f"{settings.API_ENDPOINT.rstrip('/')}/{action}/{settings.API_KEY}"
    # Ensure call attribute is present in payload
    if "call" not in payload:
        payload["call"] = action
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API Error {e.response.status_code}: {e.response.text}",
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
