from fastapi import FastAPI
from database import connect_db, disconnect_db
from routers import users, shipments, apiinfo, quotations

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VexONE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://vexone.duckdns.org",
        "https://vexone.duckdns.org:50017",
        "https://www.vexone.it",
        "https://vexone.it",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup_event():
    connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    disconnect_db()


app.include_router(users.router)
app.include_router(shipments.router)
app.include_router(apiinfo.router)
app.include_router(quotations.router)


@app.get("/")
async def root():
    return {"message": "Welcome to VexONE API"}
