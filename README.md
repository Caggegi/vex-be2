# VexONE API Project

This is a FastAPI project connected to a MongoDB database "vexONE".
It manages Users and Shipments.

## Setup

1.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    The application uses default settings. You can override them by setting environment variables:
    - `MONGO_URL`: MongoDB connection string (default: `mongodb://localhost:27018/VexONE`)
    - `SECRET_KEY`: Secret key for JWT (default: `supersecretkey`)

## Running the Application

Run the server with `uvicorn`:

```bash
uvicorn main:app --reload
```

## API Documentation

Once running, access the interactive API docs at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Endpoints

#### Authentication & Users (`/users`)

| Method | Endpoint | Description | Input (Body/Form) | Output |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/users/register` | Register a new user | **JSON**: `{ "email": "user@example.com", "password": "password123", "profile": { "first_name": "Mario", "last_name": "Rossi", "phone": "+39..." } }` | `{ "message": "User created successfully", "user_id": "..." }` |
| `POST` | `/users/login` | Login to get access token | **Form Data**: `username` (email), `password` | `{ "access_token": "...", "token_type": "bearer" }` |
| `GET` | `/users/me` | Get current user profile | **Headers**: `Authorization: Bearer <token>` | User Object (id, email, profile, addresses, etc.) |
| `PUT` | `/users/me` | Update user profile/addresses | **Headers**: `Authorization: Bearer <token>`<br>**JSON**: `{ "profile": { ... }, "default_address": { "street": "...", "city": "...", "zip": "...", "country": "..." }, "vat_address": { ... } }` | Updated User Object |

#### Shipments (`/shipments`)

All shipment endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Input (Body) | Output |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/shipments/` | Create a new shipment | **JSON**: `{ "tracking_code": "IT-123", "status": "created", "sender": { ... }, "recipient": { ... }, "package_details": { ... }, "cost": { ... } }` | Created Shipment Object |
| `GET` | `/shipments/` | Get all shipments for user | None | List of Shipment Objects |
| `GET` | `/shipments/{id}` | Get specific shipment | Path Param: `id` | Shipment Object |
| `PUT` | `/shipments/{id}` | Update a shipment | Path Param: `id`<br>**JSON**: `{ "status": "in_transit", "tracking_history": [ ... ] }` (Partial updates allowed) | Updated Shipment Object |
| `DELETE` | `/shipments/{id}` | Delete a shipment | Path Param: `id` | 204 No Content |

## Project Structure

- `main.py`: Entry point of the application.
- `models/`: MongoEngine models (ODM).
- `schemas/`: Marshmallow schemas (validation) & Pydantic models (API docs).
- `routers/`: API route handlers.
- `auth/`: Authentication logic (JWT, password hashing).
- `database.py`: Database connection logic.
- `config.py`: Configuration settings.
