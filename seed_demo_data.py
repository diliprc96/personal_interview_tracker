from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta

from sqlalchemy import select

from app.database import configure_database, get_session_factory, init_db
from app.enums import ActionRequired, PipelineStage, Priority
from app.models import Candidate


def build_demo_candidates() -> list[Candidate]:
    now = datetime.now().replace(microsecond=0)
    return [
        Candidate(
            name="Ananya Rao",
            position="GenAI Engineer",
            priority=Priority.HIGH,
            pipeline_stage=PipelineStage.TO_BE_SCHEDULED,
            action_required=ActionRequired.SCHEDULE,
            notes="Strong Python and LLM foundations.",
        ),
        Candidate(
            name="Rohit Menon",
            position="MLOps Engineer",
            priority=Priority.MEDIUM,
            pipeline_stage=PipelineStage.SCHEDULED,
            action_required=ActionRequired.NONE,
            next_interview_datetime=now + timedelta(days=1, hours=2),
            current_round="Tech 1",
            notes="Needs deeper K8s discussion.",
        ),
        Candidate(
            name="Sara Khan",
            position="Backend Engineer",
            priority=Priority.HIGH,
            pipeline_stage=PipelineStage.INTERVIEW_COMPLETED,
            action_required=ActionRequired.DECIDE,
            current_round="Tech 2",
            notes="Good design clarity, review coding speed.",
        ),
        Candidate(
            name="Vikram Joshi",
            position="Data Engineer",
            priority=Priority.LOW,
            pipeline_stage=PipelineStage.ON_HOLD,
            action_required=ActionRequired.FOLLOW_UP,
            notes="Awaiting salary alignment.",
        ),
        Candidate(
            name="Neha Iyer",
            position="GenAI Engineer",
            priority=Priority.MEDIUM,
            pipeline_stage=PipelineStage.OFFERED,
            action_required=ActionRequired.FOLLOW_UP,
            expected_joining_date=date.today() + timedelta(days=10),
            notes="Offer shared, waiting final confirmation.",
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo data for Interview Tracker")
    parser.add_argument("--force", action="store_true", help="Add demo data even if candidates already exist")
    args = parser.parse_args()

    configure_database()
    init_db()
    session_factory = get_session_factory()

    with session_factory() as db:
        existing_count = len(list(db.scalars(select(Candidate.id)).all()))
        if existing_count > 0 and not args.force:
            print("Skipped seeding because candidate data already exists. Use --force to insert anyway.")
            return

        demo_candidates = build_demo_candidates()
        db.add_all(demo_candidates)
        db.commit()
        print(f"Seeded {len(demo_candidates)} demo candidates.")


if __name__ == "__main__":
    main()
