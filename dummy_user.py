from models.user import User, UserProfile
from bson import ObjectId
from datetime import datetime

def get_dummy_user():
    profile = UserProfile(
        first_name="DEV",
        last_name="VEXONE",
        phone="+393331234567",
        vat_number=""
    )
    # Note: 'id' in MongoEngine is usually the primary key. 
    # We can pass it as 'id' or 'pk' to the constructor if we want to simulate the object fully.
    # However, MongoEngine documents might not accept 'id' in __init__ if it's not defined as a field explicitly, 
    # but usually they accept **kwargs.
    # Let's try to set it after creation if needed, or pass it.
    
    user = User(
        email="dev@vex.it",
        password_hash="$2b$12$fUlRWHl/ID9PWx1/VxxBheiPvYhIsedueef4XBoM/yZ58WM8vWrb.",
        role="customer",
        profile=profile,
        created_at=datetime(2025, 11, 25, 20, 53, 18, 624000),
        updated_at=datetime(2025, 11, 25, 20, 53, 18, 624000)
    )
    user.id = ObjectId("6926173e8e485aa8c9ec65fa")
    return user
