from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_client, get_current_worker
from database import get_db
from geocoding import geocode_address, haversine_distance_km

router = APIRouter(prefix="/issues", tags=["issues"])

NEARBY_RADIUS_KM = 5.0


@router.post("", response_model=schemas.Issue, status_code=status.HTTP_201_CREATED)
def create_issue(
    payload: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_client: models.Client = Depends(get_current_client),
):
    if payload.latitude is not None and payload.longitude is not None:
        coords = (payload.latitude, payload.longitude)
    else:
        coords = geocode_address(payload.location_text)

    if coords is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not geocode the given location",
        )

    issue = models.Issue(
        client_id=current_client.client_id,
        category=payload.category,
        description=payload.description,
        photo_url=payload.photo_url,
        location_text=payload.location_text,
        latitude=coords[0],
        longitude=coords[1],
        status=models.IssueStatus.pending,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("/mine/client", response_model=List[schemas.Issue])
def list_my_issues_as_client(
    db: Session = Depends(get_db),
    current_client: models.Client = Depends(get_current_client),
):
    return (
        db.query(models.Issue)
        .filter(models.Issue.client_id == current_client.client_id)
        .order_by(models.Issue.created_at.desc())
        .all()
    )


@router.get("/mine/worker", response_model=List[schemas.Issue])
def list_my_issues_as_worker(
    db: Session = Depends(get_db),
    current_worker: models.Worker = Depends(get_current_worker),
):
    return (
        db.query(models.Issue)
        .filter(models.Issue.accepted_by == current_worker.worker_id)
        .order_by(models.Issue.created_at.desc())
        .all()
    )


@router.get("/nearby", response_model=List[schemas.Issue])
def list_nearby_issues(
    db: Session = Depends(get_db),
    current_worker: models.Worker = Depends(get_current_worker),
):
    if current_worker.latitude is None or current_worker.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Worker location is not set; cannot compute nearby jobs",
        )

    if current_worker.status != models.WorkerStatus.available:
        return []

    candidates = (
        db.query(models.Issue)
        .filter(
            models.Issue.category == current_worker.category,
            models.Issue.status == models.IssueStatus.pending,
            models.Issue.latitude.isnot(None),
            models.Issue.longitude.isnot(None),
        )
        .all()
    )

    worker_lat = float(current_worker.latitude)
    worker_lon = float(current_worker.longitude)

    nearby = [
        issue
        for issue in candidates
        if haversine_distance_km(worker_lat, worker_lon, float(issue.latitude), float(issue.longitude))
        <= NEARBY_RADIUS_KM
    ]
    return nearby


@router.get("/{issue_id}/worker", response_model=schemas.Worker)
def get_issue_worker(
    issue_id: int,
    db: Session = Depends(get_db),
    current_client: models.Client = Depends(get_current_client),
):
    issue = db.query(models.Issue).filter(models.Issue.issue_id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    if issue.client_id != current_client.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your issue")

    if issue.worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No worker has accepted this job yet")

    return issue.worker


@router.post("/{issue_id}/accept", response_model=schemas.Issue)
def accept_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_worker: models.Worker = Depends(get_current_worker),
):
    issue = (
        db.query(models.Issue)
        .filter(models.Issue.issue_id == issue_id)
        .with_for_update()
        .first()
    )
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    if issue.category != current_worker.category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category mismatch")

    if issue.status != models.IssueStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job already taken")

    issue.status = models.IssueStatus.accepted
    issue.accepted_by = current_worker.worker_id
    issue.accepted_at = datetime.utcnow()
    current_worker.status = models.WorkerStatus.busy
    db.commit()
    db.refresh(issue)
    return issue


@router.post("/{issue_id}/complete", response_model=schemas.Issue)
def complete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_client: models.Client = Depends(get_current_client),
):
    issue = db.query(models.Issue).filter(models.Issue.issue_id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    if issue.client_id != current_client.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your issue")

    if issue.status != models.IssueStatus.accepted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only an accepted job can be marked completed",
        )

    issue.status = models.IssueStatus.completed
    issue.completed_at = datetime.utcnow()
    if issue.worker is not None:
        issue.worker.status = models.WorkerStatus.available
    db.commit()
    db.refresh(issue)
    return issue


@router.post("/{issue_id}/cancel", response_model=schemas.Issue)
def cancel_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_client: models.Client = Depends(get_current_client),
):
    issue = db.query(models.Issue).filter(models.Issue.issue_id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    if issue.client_id != current_client.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your issue")

    if issue.status != models.IssueStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only a pending job (not yet accepted by a worker) can be cancelled",
        )

    issue.status = models.IssueStatus.cancelled
    db.commit()
    db.refresh(issue)
    return issue
