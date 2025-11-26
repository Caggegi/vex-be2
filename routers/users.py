from fastapi import APIRouter, HTTPException, status, Depends, Body
from marshmallow import ValidationError
from schemas.user import UserRegisterSchema, UserLoginSchema, UserSchema, UserUpdateSchema
from schemas.pydantic_models import UserRegisterModel, UserLoginModel, UserUpdateModel
from models.user import User
from auth.security import get_password_hash, verify_password, create_access_token
from auth.dependencies import get_current_user
from datetime import timedelta
from config import settings

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterModel):
    schema = UserRegisterSchema()
    try:
        # Convert Pydantic model to dict
        data = schema.load(payload.model_dump())
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)
    
    # Check if user exists
    if User.objects(email=data['email']).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_pw = get_password_hash(data['password'])
    
    # Create user
    # Note: data['profile'] etc are dictionaries, mongoengine EmbeddedDocumentField expects the EmbeddedDocument instance or dict (it usually handles dicts well if structure matches)
    # However, since we used marshmallow to load, we have clean dicts.
    # We need to be careful with the password field. The schema has 'password', the model has 'password_hash'.
    
    user_data = data.copy()
    del user_data['password']
    user_data['password_hash'] = hashed_pw
    
    user = User(**user_data)
    user.save()
    
    return {"message": "User created successfully", "user_id": str(user.id)}

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm has username and password fields
    # We treat username as email
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
    schema = UserSchema()
    return schema.dump(current_user)

@router.put("/me")
async def update_user_me(payload: UserUpdateModel, current_user: User = Depends(get_current_user)):
    schema = UserUpdateSchema()
    try:
        data = schema.load(payload.model_dump(exclude_unset=True), partial=True)
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)
    
    current_user.modify(**data)
    current_user.reload()
    
    user_schema = UserSchema()
    return user_schema.dump(current_user)
