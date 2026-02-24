from models.user import User, Person, Address, History
from bson import ObjectId
from datetime import datetime

def get_dummy_user():
    address = Address(
        country="Italy",
        zip="00100",
        city="Rome",
        address="Via del Corso",
        number=1
    )
    info = Person(
        name="DEV",
        surname="VEXONE",
        address=[address]
    )
    
    user = User(
        email="dev@vex.it",
        password_hash="$2b$12$fUlRWHl/ID9PWx1/VxxBheiPvYhIsedueef4XBoM/yZ58WM8vWrb.",
        type="admin",
        info=info,
        credit=100.0,
        history=History(shippings=[], credits=[]),
        clients=Person(name="Client", surname="Demo", address=[]),
        created_at=datetime(2025, 11, 25, 20, 53, 18, 624000),
        updated_at=datetime(2025, 11, 25, 20, 53, 18, 624000)
    )
    user.id = ObjectId("6926173e8e485aa8c9ec65fa")
    return user
