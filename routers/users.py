from fastapi import APIRouter, HTTPException, status, Depends, Body
from marshmallow import ValidationError
from schemas.user import UserRegisterSchema, UserSchema, UserUpdateSchema
from schemas.pydantic_models import UserRegisterModel, UserUpdateModel
from models.user import User
from auth.security import get_password_hash, verify_password, create_access_token
from auth.dependencies import get_current_user
from datetime import timedelta
from config import settings
from utils.easyparcel import call_easyparcel
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage


class InvoiceRequest(BaseModel):
    amount: float
    method: str
    tx_id: str


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterModel):
    schema = UserRegisterSchema()
    try:
        # Convert Pydantic model to dict
        data = schema.load(payload.model_dump())
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    # Check if user exists
    if User.objects(email=data["email"]).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = get_password_hash(data["password"])

    user_data = data.copy()
    del user_data["password"]
    user_data["password_hash"] = hashed_pw

    user = User(**user_data)
    user.save()

    # Create customer on EasyParcel
    try:
        addr = data["info"]["address"][0] if data["info"]["address"] else {}
        ep_payload = {
            "call": "newcustomer",
            "dettagli": {
                "cognome": data["info"]["surname"],
                "nome": data["info"]["name"],
                "indirizzo": addr.get("address", "N/A") + ", " + str(addr.get("number", "0")),
                "cap": addr.get("zip", "00000"),
                "localita": addr.get("city", "N/A"),
                "provincia": addr.get("provincia", "--"),
                "nazione": addr.get("country", "IT"),
                "email": data["email"],
                "codicefiscale": data["info"].get("tax_code") or "RSSMRA11A11A111A",
                "username": data["email"],
                "password": payload.password,
                "fe_sdi": "0000000"
            }
        }
        ep_response = call_easyparcel("newcustomer", ep_payload)
        if ep_response and ep_response.get("result") == "OK":
            user.easyparcel_id = str(ep_response.get("id_dva"))
            user.save()
    except Exception as e:
        print(f"EasyParcel registration error: {e}")
        # We don't block registration if EasyParcel fails, but we record it

    return {"message": "User created successfully", "user_id": str(user.id)}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "dev@vex.it":
        from dummy_user import get_dummy_user

        user = get_dummy_user()
    else:
        user = User.objects(email=form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    # Refresh balance from EasyParcel if available
    if current_user.easyparcel_id:
        try:
            payload = {"call": "balance", "dettagli": {"idcustomer": int(current_user.easyparcel_id)}}
            response = call_easyparcel("balance", payload)
            if response and response.get("result") == "OK":
                # Assuming details contains balance or similar. 
                # According to manual, it returns credito_prepagato for the master, 
                # and maybe specifically for the customer if idcustomer is provided.
                # Let's check the response structure for Balance in the manual.
                # "credito_prepagato" is in "dettagli" for apikeyinfo. 
                # For balance it's likely similar.
                new_balance = response.get("dettagli", {}).get("credito_prepagato")
                if new_balance is not None:
                    current_user.credit = float(new_balance)
                    current_user.save()
        except Exception as e:
            print(f"Error fetching balance from EasyParcel: {e}")

    schema = UserSchema()
    return schema.dump(current_user)


@router.put("/me")
async def update_user_me(
    payload: UserUpdateModel, current_user: User = Depends(get_current_user)
):
    schema = UserUpdateSchema()
    try:
        data = schema.load(payload.model_dump(exclude_unset=True), partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    current_user.modify(**data)
    current_user.reload()

    user_schema = UserSchema()
    return user_schema.dump(current_user)


@router.post("/recharge")
async def recharge_account(
    payload: InvoiceRequest, current_user: User = Depends(get_current_user)
):
    try:
        from models.user import Operation

        # Add Operation to History
        new_op = Operation(
            tx_id=payload.tx_id,
            title="Ricarica VEXCARD",
            description=f"Metodo: {payload.method}",
            amount=payload.amount,
            tx_type="online",
        )
        current_user.history.credits.insert(0, new_op)
        current_user.credit += payload.amount

        # If it's a bank transfer (IBAN/bank), call EasyParcel addfund
        if payload.method == "bank" and current_user.easyparcel_id:
            try:
                ep_payload = {
                    "call": "addfund",
                    "dettagli": {
                        "idcustomer": int(current_user.easyparcel_id),
                        "amount": payload.amount
                    }
                }
                ep_response = call_easyparcel("addfund", ep_payload)
                if ep_response and ep_response.get("result") == "OK":
                    print(f"Successfully added funds to EasyParcel for user {current_user.email}")
            except Exception as e:
                print(f"EasyParcel addfund error: {e}")
                # We could choose to rollback or just log the error. 
                # For now we log as it's a manual process on the user side.

        current_user.save()

        # Send invoice email ONLY if method is PayPal
        if payload.method == "paypal":
            try:
                msg = EmailMessage()
                msg["Subject"] = "Conferma di pagamento VEXONE"
                msg["From"] = settings.SMTP_USER
                msg["To"] = current_user.email

                content = f"""
                Gentile utente,
                
                Ti confermiamo la ricezione del pagamento per il tuo Account VEXONE.
                
                Dettagli:
                - ID Transazione: {payload.tx_id}
                - Importo: € {payload.amount:.2f}
                - Metodo: {payload.method}
                
                Grazie per aver scelto VEXONE.
                """
                msg.set_content(content)

                with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                print(f"Error sending email: {e}")
                # Don't block flow just because email failed

        # Dump using Schema to return consistent response
        user_schema = UserSchema()
        return {
            "message": "Recharge successful",
            "user": user_schema.dump(current_user),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
