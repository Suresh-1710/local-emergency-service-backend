from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from auth import create_access_token, hash_password, verify_password
from database import get_db
from geocoding import geocode_address

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/client/signup", response_model=schemas.Client, status_code=status.HTTP_201_CREATED)
def client_signup(payload: schemas.ClientCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Client).filter(models.Client.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")

    if payload.latitude is not None and payload.longitude is not None:
        coords = (payload.latitude, payload.longitude)
    else:
        coords = geocode_address(payload.home_address_text)

    client = models.Client(
        name=payload.name,
        home_address_text=payload.home_address_text,
        latitude=coords[0] if coords else None,
        longitude=coords[1] if coords else None,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.post("/client/login", response_model=schemas.Token)
def client_login(payload: schemas.ClientLogin, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.phone == payload.phone).first()
    if not client or not verify_password(payload.password, client.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone or password")

    token = create_access_token({"sub": str(client.client_id), "role": "client"})
    return schemas.Token(access_token=token)


@router.post("/worker/signup", response_model=schemas.Worker, status_code=status.HTTP_201_CREATED)
def worker_signup(payload: schemas.WorkerCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Worker).filter(models.Worker.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")

    if payload.latitude is not None and payload.longitude is not None:
        coords = (payload.latitude, payload.longitude)
    else:
        coords = geocode_address(payload.location_text)

    worker = models.Worker(
        name=payload.name,
        age=payload.age,
        experience_years=payload.experience_years,
        category=payload.category,
        location_text=payload.location_text,
        latitude=coords[0] if coords else None,
        longitude=coords[1] if coords else None,
        photo_url=payload.photo_url,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.post("/worker/login", response_model=schemas.Token)
def worker_login(payload: schemas.WorkerLogin, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).filter(models.Worker.phone == payload.phone).first()
    if not worker or not verify_password(payload.password, worker.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone or password")

    token = create_access_token({"sub": str(worker.worker_id), "role": "worker"})
    return schemas.Token(access_token=token)
