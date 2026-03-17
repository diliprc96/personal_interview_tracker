from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum as SAEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base
from app.enums import ActionRequired, PipelineStage, Priority


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    position: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    pipeline_stage: Mapped[PipelineStage] = mapped_column(
        SAEnum(PipelineStage, name="pipeline_stage", native_enum=False, validate_strings=True, create_constraint=True),
        nullable=False,
        default=PipelineStage.TO_BE_SCHEDULED,
        server_default=PipelineStage.TO_BE_SCHEDULED.value,
        index=True,
    )
    action_required: Mapped[ActionRequired] = mapped_column(
        SAEnum(ActionRequired, name="action_required", native_enum=False, validate_strings=True, create_constraint=True),
        nullable=False,
        default=ActionRequired.SCHEDULE,
        server_default=ActionRequired.SCHEDULE.value,
        index=True,
    )
    priority: Mapped[Priority] = mapped_column(
        SAEnum(Priority, name="priority", native_enum=False, validate_strings=True, create_constraint=True),
        nullable=False,
        default=Priority.MEDIUM,
        server_default=Priority.MEDIUM.value,
        index=True,
    )
    next_interview_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    expected_joining_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    current_round: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.current_timestamp(),
        index=True,
    )
