from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import distinct, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.enums import ActionRequired, PipelineStage, Priority
from app.models import Candidate
from app.schemas import CalendarResponse, CandidateCreate, CandidateRead, CandidateUpdate, MetadataResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["candidates"])


@router.get("/metadata", response_model=MetadataResponse)
def get_metadata(db: Session = Depends(get_db)) -> MetadataResponse:
    positions = list(db.scalars(select(distinct(Candidate.position)).order_by(Candidate.position.asc())).all())
    return MetadataResponse(
        pipeline_stage_values=list(PipelineStage),
        action_required_values=list(ActionRequired),
        priority_values=list(Priority),
        positions=positions,
    )


@router.get("/candidates", response_model=list[CandidateRead])
def get_candidates(
    position: str | None = None,
    pipeline_stage: PipelineStage | None = None,
    action_required: ActionRequired | None = None,
    next_interview_from: datetime | None = None,
    next_interview_to: datetime | None = None,
    expected_joining_from: date | None = None,
    expected_joining_to: date | None = None,
    sort_by: Literal["priority", "next_interview_datetime", "expected_joining_date", "updated_at", "name"] = "updated_at",
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
) -> list[CandidateRead]:
    candidates = crud.list_candidates(
        db,
        position=position,
        pipeline_stage=pipeline_stage.value if pipeline_stage else None,
        action_required=action_required,
        next_interview_from=next_interview_from,
        next_interview_to=next_interview_to,
        expected_joining_from=expected_joining_from,
        expected_joining_to=expected_joining_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return [CandidateRead.model_validate(candidate) for candidate in candidates]


@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)) -> CandidateRead:
    candidate = crud.get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return CandidateRead.model_validate(candidate)


@router.post("/candidates", response_model=CandidateRead, status_code=status.HTTP_201_CREATED)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)) -> CandidateRead:
    try:
        candidate = crud.create_candidate(db, payload)
    except IntegrityError as exc:
        logger.warning("Failed to create candidate due to integrity error: %s", exc)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid candidate data") from exc
    return CandidateRead.model_validate(candidate)


@router.patch("/candidates/{candidate_id}", response_model=CandidateRead)
def patch_candidate(candidate_id: int, payload: CandidateUpdate, db: Session = Depends(get_db)) -> CandidateRead:
    candidate = crud.get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    try:
        updated = crud.update_candidate(db, candidate, payload)
    except IntegrityError as exc:
        logger.warning("Failed to update candidate %s due to integrity error: %s", candidate_id, exc)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid update payload") from exc

    return CandidateRead.model_validate(updated)


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def remove_candidate(candidate_id: int, db: Session = Depends(get_db)) -> Response:
    candidate = crud.get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    crud.delete_candidate(db, candidate)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/action-items", response_model=list[CandidateRead])
def get_action_items(db: Session = Depends(get_db)) -> list[CandidateRead]:
    candidates = crud.list_action_items(db)
    return [CandidateRead.model_validate(candidate) for candidate in candidates]


@router.get("/calendar", response_model=CalendarResponse)
def get_calendar(
    window: Literal["today", "week"] = Query(default="today"),
    include_joining: bool = True,
    db: Session = Depends(get_db),
) -> CalendarResponse:
    interviews, joinings = crud.get_calendar_candidates(db, window=window, include_joining=include_joining)
    return CalendarResponse(
        interviews=[CandidateRead.model_validate(candidate) for candidate in interviews],
        joinings=[CandidateRead.model_validate(candidate) for candidate in joinings],
    )
