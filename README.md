# Interview Tracker

A small, reliable web application for tracking candidates through an interview pipeline.

## Documentation

- Release checklist: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md)
- End-user guide: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

## Stack

- Backend: FastAPI
- Database: SQLite
- Frontend: Server-hosted HTML/CSS/JavaScript (no frontend build step)
- Tests: pytest + FastAPI TestClient

## Features

- Add and update candidates
- Main list with filters and sorting
- Inline edits for stage, action required, and priority
- Candidate detail editor for full updates
- Action Items view (`action_required != NONE`) with focused columns
- Today / This Week view with planning-focused columns
- Data operations from UI: export CSV, import CSV/XLSX, and clear all data
- REST API with validation and explicit status codes

## Data Model

Single core table: `Candidate`

Fields:
- `id`
- `name`
- `position`
- `pipeline_stage`
- `action_required`
- `priority`
- `next_interview_datetime`
- `expected_joining_date`
- `current_round`
- `notes`
- `created_at`
- `updated_at`

Defaults on create:
- `pipeline_stage = TO_BE_SCHEDULED`
- `action_required = SCHEDULE`
- `priority = MEDIUM`

## Run Locally

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   python main.py
   ```

4. Open:
   - Web UI: http://127.0.0.1:8000
   - API docs: http://127.0.0.1:8000/docs

SQLite DB file (`interview_tracker.db`) is created automatically in the project root.

## Sharing and Packaging (Safran-Friendly)

Given constraints:
- Docker is not allowed.
- Batch scripts must be shared in a ZIP.

Recommended model:
- Keep this repository as the source of truth for continuous improvement.
- Distribute a ZIP package for non-technical users.

### Option A: Technical users (GitHub flow)

1. Clone repository.
2. Run `python main.py` or `start_tracker.cmd`.
3. Open `http://127.0.0.1:8000`.

### Option B: Non-technical users (ZIP flow)

1. Download the latest ZIP package (from GitHub Release or internal file share).
2. Extract ZIP to a local folder.
3. Double-click `start_tracker.cmd`.
4. Browser opens automatically at `http://127.0.0.1:8000`.

### Build a release ZIP

From project root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/make_release_zip.ps1
```

Output:
- ZIP file in `dist/` with timestamp in filename.

### Optional demo data

After startup, populate sample records:

```powershell
python seed_demo_data.py
```

To force add demo data even if records exist:

```powershell
python seed_demo_data.py --force
```

## API Endpoints

- `GET /api/candidates`
- `GET /api/candidates/{id}`
- `POST /api/candidates`
- `PATCH /api/candidates/{id}`
- `DELETE /api/candidates/{id}`
- `GET /api/action-items`
- `GET /api/calendar`
- `GET /api/metadata`
- `GET /api/candidates-export`
- `POST /api/candidates-import`
- `POST /api/candidates-clear`

Useful `GET /api/candidates` query params:
- `position`
- `pipeline_stage`
- `action_required`
- `next_interview_from`
- `next_interview_to`
- `expected_joining_from`
- `expected_joining_to`
- `sort_by`
- `sort_order`

## Testing

Run tests:

```powershell
pytest -q
```

Coverage focus:
- Candidate creation defaults
- Enum and required-field validation
- Filtering logic (action/date)
- API happy path and error path behavior

## Logging and Error Handling

- App-level logging is enabled with timestamp, level, logger, and message.
- Validation failures return 422 with structured details.
- Unexpected server errors are logged and return a safe 500 response.
