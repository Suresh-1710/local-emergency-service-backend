import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/client/login")
worker_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/worker/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


def get_current_client(
    token: str = Depends(client_oauth2_scheme), db: Session = Depends(get_db)
) -> models.Client:
    payload = _decode_token(token)
    if payload.get("role") != "client":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a client token")
    client_id = payload.get("sub")
    client = db.query(models.Client).filter(models.Client.client_id == int(client_id)).first()
    if client is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client not found")
    return client


def get_current_worker(
    token: str = Depends(worker_oauth2_scheme), db: Session = Depends(get_db)
) -> models.Worker:
    payload = _decode_token(token)
    if payload.get("role") != "worker":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a worker token")
    worker_id = payload.get("sub")
    worker = db.query(models.Worker).filter(models.Worker.worker_id == int(worker_id)).first()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Worker not found")
    return worker
