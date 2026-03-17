from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import ActionRequired, PipelineStage, Priority


class CandidateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=120)
    priority: Priority = Priority.MEDIUM
    notes: str = Field(default="", max_length=4000)

    @field_validator("name", "position")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str) -> str:
        return value.strip()


class CandidateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    position: str | None = Field(default=None, min_length=1, max_length=120)
    pipeline_stage: PipelineStage | None = None
    action_required: ActionRequired | None = None
    priority: Priority | None = None
    next_interview_datetime: datetime | None = None
    expected_joining_date: date | None = None
    current_round: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("name", "position", "current_round")
    @classmethod
    def strip_optional_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        return value

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    position: str
    pipeline_stage: PipelineStage
    action_required: ActionRequired
    priority: Priority
    next_interview_datetime: datetime | None
    expected_joining_date: date | None
    current_round: str | None
    notes: str
    created_at: datetime
    updated_at: datetime


class MetadataResponse(BaseModel):
    pipeline_stage_values: list[PipelineStage]
    action_required_values: list[ActionRequired]
    priority_values: list[Priority]
    positions: list[str]


class CalendarResponse(BaseModel):
    interviews: list[CandidateRead]
    joinings: list[CandidateRead]
