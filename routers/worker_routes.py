from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_worker
from database import get_db

router = APIRouter(prefix="/workers", tags=["workers"])


@router.patch("/me/status", response_model=schemas.Worker)
def update_my_status(
    payload: schemas.WorkerStatusUpdate,
    db: Session = Depends(get_db),
    current_worker: models.Worker = Depends(get_current_worker),
):
    current_worker.status = payload.status
    db.commit()
    db.refresh(current_worker)
    return current_worker
