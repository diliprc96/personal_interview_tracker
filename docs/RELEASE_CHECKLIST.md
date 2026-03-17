# Release Checklist - Interview Tracker

Use this checklist before sharing a new version with end users.

## 1. Release Metadata

- [ ] Version tag decided (example: `v1.0.0`)
- [ ] Release date confirmed
- [ ] Change summary prepared (2-5 bullets)

## 2. Quality Gates

- [ ] Run tests: `python -m pytest -q`
- [ ] App startup check: `python main.py`
- [ ] UI smoke test completed:
  - [ ] Add candidate
  - [ ] Edit candidate inline
  - [ ] Update candidate in detail panel
  - [ ] Action Items view opens and loads
  - [ ] Today/This Week view opens and loads

## 3. Packaging

- [ ] Build ZIP package:
  - `powershell -ExecutionPolicy Bypass -File scripts/make_release_zip.ps1`
- [ ] Confirm ZIP created in `dist/`
- [ ] Extract ZIP and test launcher:
  - [ ] Double-click `start_tracker.cmd`
  - [ ] Browser opens at `http://127.0.0.1:8000`

## 4. Documentation

- [ ] `README.md` updated if setup steps changed
- [ ] `docs/USER_GUIDE.md` updated if UI flow changed
- [ ] Screenshots refreshed in `docs/images/` if significant UI changes were made

## 5. Distribution

- [ ] Upload ZIP to approved internal channel (or GitHub Release for technical audience)
- [ ] Share short release note with:
  - Version
  - What changed
  - Any user action required

## 6. Rollback Plan

- [ ] Keep previous stable ZIP accessible
- [ ] If issue reported, ask user to run previous ZIP immediately
- [ ] Create bug ticket with repro steps and logs

## Suggested Release Note Template

Version: `<version>`

Changes:
- <change 1>
- <change 2>
- <change 3>

How to run:
1. Extract ZIP
2. Double-click `start_tracker.cmd`
3. Open `http://127.0.0.1:8000`
