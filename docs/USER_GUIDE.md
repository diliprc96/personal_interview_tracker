# Interview Tracker - User Guide

This guide is for non-technical users who receive a ZIP package of the app.

## 1. What this tool does

Interview Tracker helps you:
- Add candidates quickly
- Track each candidate's interview stage
- See action items that need attention
- View interviews planned for today or this week

## 2. Start the app (ZIP method)

1. Extract the ZIP file to a local folder.
2. Open the extracted folder.
3. Double-click `start_tracker.cmd`.
4. Wait for the browser to open automatically.
5. Use the app at `http://127.0.0.1:8000`.

Note:
- Keep the command window open while using the app.
- To stop the app, press `Ctrl + C` in that window.

## 3. Main views

### Control Center

Use this as your main working screen.
- See all candidates in one table
- Filter by position, stage, and action
- Sort by priority or dates
- Edit stage/action/priority inline from dropdowns

![Control Center](images/control-center.png)

### Candidate Detail

Click any row in Control Center to open full details.

Update:
- Pipeline stage
- Action required
- Priority
- Next interview date/time
- Expected joining date
- Current round
- Notes

Read-only:
- Created at
- Updated at

![Candidate Detail](images/candidate-detail.png)

### Action Items

Shows only candidates where action is required.

Groups:
- SCHEDULE
- RESCHEDULE
- DECIDE
- FOLLOW_UP

![Action Items](images/action-items.png)

### Today / This Week

Use this for planning interviews and near-term joins.

- Interviews for today or next 7 days
- Optional expected joining list

![Today or This Week](images/calendar-view.png)

## 4. Typical workflow

1. Add new candidate from the top form.
2. Set interview schedule and current round.
3. After interview, mark `INTERVIEW_COMPLETED` and set action to `DECIDE`.
4. Record final decision (`SELECTED`, `REJECTED`, `ON_HOLD`, or `CANCELLED`).
5. For selected candidates, track offer and expected joining date.

## 5. Common issues and fixes

App page does not open:
- Wait 20-40 seconds after first launch (initial setup may take time).
- Check command window for errors.
- Re-run `start_tracker.cmd`.

Port already in use:
- Close previous command window running this app.
- Re-run `start_tracker.cmd`.

No data visible:
- Confirm filters are not restricting results.
- Reset filters to `All`.

## 6. Data notes

- Data is stored locally in `interview_tracker.db`.
- Keep that file in the same folder for continuity.
- For backup, copy the database file periodically.

## 7. For support

When reporting issues, share:
- What action you performed
- What you expected
- What happened instead
- Any message shown in the command window
