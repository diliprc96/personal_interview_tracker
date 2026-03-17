from enum import Enum


class PipelineStage(str, Enum):
    TO_BE_SCHEDULED = "TO_BE_SCHEDULED"
    SCHEDULED = "SCHEDULED"
    INTERVIEW_COMPLETED = "INTERVIEW_COMPLETED"
    SELECTED = "SELECTED"
    OFFERED = "OFFERED"
    JOINED = "JOINED"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"


class ActionRequired(str, Enum):
    NONE = "NONE"
    SCHEDULE = "SCHEDULE"
    RESCHEDULE = "RESCHEDULE"
    DECIDE = "DECIDE"
    FOLLOW_UP = "FOLLOW_UP"


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
