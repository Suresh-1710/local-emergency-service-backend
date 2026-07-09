from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_client, get_current_worker
from database import Base, engine, get_db
from geocoding import reverse_geocode
from routers.auth_routes import router as auth_router
from routers.issue_routes import router as issue_router
from routers.upload_routes import router as upload_router, UPLOAD_DIR
from routers.worker_routes import router as worker_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Local Emergency Service Connect")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+|https://[a-zA-Z0-9-]+\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(issue_router)
app.include_router(worker_router)
app.include_router(upload_router)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}


@app.get("/geocode/reverse")
def reverse_geocode_endpoint(lat: float, lon: float):
    address = reverse_geocode(lat, lon)
    return {"address": address}


@app.get("/me/client", response_model=schemas.Client)
def read_current_client(current_client: models.Client = Depends(get_current_client)):
    return current_client


@app.get("/me/worker", response_model=schemas.Worker)
def read_current_worker(current_worker: models.Worker = Depends(get_current_worker)):
    return current_worker
