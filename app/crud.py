from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy import case, delete, select
from sqlalchemy.orm import Session

from app.enums import ActionRequired, PipelineStage, Priority
from app.models import Candidate
from app.schemas import CandidateCreate, CandidateUpdate


def create_candidate(db: Session, payload: CandidateCreate) -> Candidate:
    candidate = Candidate(
        name=payload.name,
        position=payload.position,
        priority=payload.priority,
        notes=payload.notes,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def apply_stage_defaults(candidate: Candidate, stage_was_updated: bool, action_was_updated: bool) -> None:
    if not stage_was_updated:
        return

    stage = candidate.pipeline_stage
    if stage == PipelineStage.TO_BE_SCHEDULED and not action_was_updated:
        candidate.action_required = ActionRequired.SCHEDULE
    elif stage == PipelineStage.SCHEDULED and candidate.next_interview_datetime and not action_was_updated:
        candidate.action_required = ActionRequired.NONE
    elif stage == PipelineStage.INTERVIEW_COMPLETED and not action_was_updated:
        candidate.action_required = ActionRequired.DECIDE
    elif stage in {PipelineStage.SELECTED, PipelineStage.OFFERED} and not action_was_updated:
        candidate.action_required = ActionRequired.FOLLOW_UP
    elif stage in {PipelineStage.JOINED, PipelineStage.REJECTED, PipelineStage.CANCELLED} and not action_was_updated:
        candidate.action_required = ActionRequired.NONE


def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
    return db.get(Candidate, candidate_id)


def list_candidates(
    db: Session,
    position: str | None = None,
    pipeline_stage: str | None = None,
    action_required: ActionRequired | None = None,
    next_interview_from: datetime | None = None,
    next_interview_to: datetime | None = None,
    expected_joining_from: date | None = None,
    expected_joining_to: date | None = None,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
) -> list[Candidate]:
    query = select(Candidate)

    if position:
        query = query.where(Candidate.position == position)
    if pipeline_stage:
        query = query.where(Candidate.pipeline_stage == pipeline_stage)
    if action_required:
        query = query.where(Candidate.action_required == action_required)
    if next_interview_from:
        query = query.where(Candidate.next_interview_datetime >= next_interview_from)
    if next_interview_to:
        query = query.where(Candidate.next_interview_datetime <= next_interview_to)
    if expected_joining_from:
        query = query.where(Candidate.expected_joining_date >= expected_joining_from)
    if expected_joining_to:
        query = query.where(Candidate.expected_joining_date <= expected_joining_to)

    priority_rank = case(
        (Candidate.priority == Priority.HIGH, 1),
        (Candidate.priority == Priority.MEDIUM, 2),
        else_=3,
    )

    sort_map = {
        "priority": priority_rank,
        "next_interview_datetime": Candidate.next_interview_datetime,
        "expected_joining_date": Candidate.expected_joining_date,
        "updated_at": Candidate.updated_at,
        "name": Candidate.name,
    }
    sort_expr = sort_map.get(sort_by, Candidate.updated_at)

    if sort_order.lower() == "asc":
        query = query.order_by(sort_expr.asc(), Candidate.updated_at.desc())
    else:
        query = query.order_by(sort_expr.desc(), Candidate.updated_at.desc())

    return list(db.scalars(query).all())


def update_candidate(db: Session, candidate: Candidate, payload: CandidateUpdate) -> Candidate:
    update_values = payload.model_dump(exclude_unset=True)
    stage_was_updated = "pipeline_stage" in update_values
    action_was_updated = "action_required" in update_values

    for field, value in update_values.items():
        setattr(candidate, field, value)

    apply_stage_defaults(candidate, stage_was_updated=stage_was_updated, action_was_updated=action_was_updated)

    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def delete_candidate(db: Session, candidate: Candidate) -> None:
    db.delete(candidate)
    db.commit()


def clear_candidates(db: Session) -> int:
    result = db.execute(delete(Candidate))
    db.commit()
    return int(result.rowcount or 0)


def list_action_items(db: Session) -> list[Candidate]:
    query = (
        select(Candidate)
        .where(Candidate.action_required != ActionRequired.NONE)
        .order_by(Candidate.action_required.asc(), Candidate.updated_at.desc())
    )
    return list(db.scalars(query).all())


def get_calendar_candidates(db: Session, window: str, include_joining: bool) -> tuple[list[Candidate], list[Candidate]]:
    today = datetime.now()
    start_of_day = datetime.combine(today.date(), time.min)

    if window == "week":
        end = start_of_day + timedelta(days=7)
    else:
        end = start_of_day + timedelta(days=1)

    interview_query = (
        select(Candidate)
        .where(Candidate.next_interview_datetime.is_not(None))
        .where(Candidate.next_interview_datetime >= start_of_day)
        .where(Candidate.next_interview_datetime < end)
        .order_by(Candidate.next_interview_datetime.asc())
    )
    interviews = list(db.scalars(interview_query).all())

    joinings: list[Candidate] = []
    if include_joining:
        joining_query = (
            select(Candidate)
            .where(Candidate.expected_joining_date.is_not(None))
            .where(Candidate.expected_joining_date >= start_of_day.date())
            .where(Candidate.expected_joining_date < end.date())
            .order_by(Candidate.expected_joining_date.asc())
        )
        joinings = list(db.scalars(joining_query).all())

    return interviews, joinings
