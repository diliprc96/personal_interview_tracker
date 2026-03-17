const state = {
    metadata: null,
    selectedCandidateId: null,
};

function setStatus(message, isError = false) {
    const statusEl = document.getElementById("status");
    statusEl.textContent = message;
    statusEl.classList.toggle("error", isError);
}

async function apiRequest(path, options = {}) {
    const response = await fetch(path, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    if (!response.ok) {
        let errorMessage = "Request failed";
        try {
            const data = await response.json();
            if (data.detail && typeof data.detail === "string") {
                errorMessage = data.detail;
            } else if (Array.isArray(data.errors) && data.errors.length > 0) {
                errorMessage = data.errors[0].msg || errorMessage;
            }
        } catch {
            errorMessage = `HTTP ${response.status}`;
        }
        throw new Error(errorMessage);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

function enumOptions(values) {
    return values.map((value) => `<option value="${value}">${value}</option>`).join("");
}

function fillSelect(selectId, values, includeAll = false) {
    const select = document.getElementById(selectId);
    const all = includeAll ? '<option value="">All</option>' : "";
    select.innerHTML = all + enumOptions(values);
}

function shortenNotes(notes) {
    if (!notes) return "";
    return notes.length > 80 ? `${notes.slice(0, 80)}...` : notes;
}

function formatDateTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
}

function formatDate(value) {
    if (!value) return "-";
    return value;
}

function toDateTimeLocal(value) {
    if (!value) return "";
    return value.slice(0, 16);
}

function getFilters() {
    const params = new URLSearchParams();

    const position = document.getElementById("filter-position").value;
    const stage = document.getElementById("filter-stage").value;
    const action = document.getElementById("filter-action").value;
    const sortBy = document.getElementById("sort-by").value;
    const sortOrder = document.getElementById("sort-order").value;

    if (position) params.set("position", position);
    if (stage) params.set("pipeline_stage", stage);
    if (action) params.set("action_required", action);
    params.set("sort_by", sortBy);
    params.set("sort_order", sortOrder);

    return params;
}

function renderInlineSelect(field, currentValue, values, candidateId) {
    const options = values
        .map((value) => `<option value="${value}" ${value === currentValue ? "selected" : ""}>${value}</option>`)
        .join("");

    return `<select data-inline-field="${field}" data-id="${candidateId}">${options}</select>`;
}

function attachInlineHandlers(container) {
    container.querySelectorAll("select[data-inline-field]").forEach((select) => {
        select.addEventListener("click", (event) => event.stopPropagation());
        select.addEventListener("change", async (event) => {
            const target = event.currentTarget;
            const candidateId = Number(target.dataset.id);
            const field = target.dataset.inlineField;
            const value = target.value;

            try {
                await apiRequest(`/api/candidates/${candidateId}`, {
                    method: "PATCH",
                    body: JSON.stringify({ [field]: value }),
                });
                setStatus("Candidate updated");
                await Promise.all([loadCandidates(), loadActionItems(), loadCalendar()]);
                if (state.selectedCandidateId === candidateId) {
                    await loadCandidateDetail(candidateId);
                }
            } catch (error) {
                setStatus(error.message, true);
            }
        });
    });
}

async function loadMetadata() {
    state.metadata = await apiRequest("/api/metadata");

    fillSelect("new-priority", state.metadata.priority_values);
    fillSelect("filter-stage", state.metadata.pipeline_stage_values, true);
    fillSelect("filter-action", state.metadata.action_required_values, true);
    fillSelect("detail-stage", state.metadata.pipeline_stage_values);
    fillSelect("detail-action", state.metadata.action_required_values);
    fillSelect("detail-priority", state.metadata.priority_values);

    const positionFilter = document.getElementById("filter-position");
    positionFilter.innerHTML = '<option value="">All</option>' + enumOptions(state.metadata.positions);
}

function renderCandidateRow(candidate) {
    return `
        <tr data-candidate-id="${candidate.id}">
            <td>${candidate.name}</td>
            <td>${candidate.position}</td>
            <td>${renderInlineSelect("pipeline_stage", candidate.pipeline_stage, state.metadata.pipeline_stage_values, candidate.id)}</td>
            <td>${renderInlineSelect("action_required", candidate.action_required, state.metadata.action_required_values, candidate.id)}</td>
            <td>${renderInlineSelect("priority", candidate.priority, state.metadata.priority_values, candidate.id)}</td>
            <td>${formatDateTime(candidate.next_interview_datetime)}</td>
            <td>${formatDate(candidate.expected_joining_date)}</td>
            <td>${shortenNotes(candidate.notes)}</td>
        </tr>
    `;
}

async function loadCandidates() {
    const params = getFilters();
    const candidates = await apiRequest(`/api/candidates?${params.toString()}`);

    const tbody = document.querySelector("#candidate-table tbody");
    tbody.innerHTML = candidates.map(renderCandidateRow).join("");

    tbody.querySelectorAll("tr[data-candidate-id]").forEach((row) => {
        row.addEventListener("click", () => {
            const candidateId = Number(row.dataset.candidateId);
            loadCandidateDetail(candidateId);
        });
    });

    attachInlineHandlers(tbody);
}

function renderSimpleTable(candidates) {
    if (!candidates.length) {
        return "<p>No candidates found.</p>";
    }

    const rows = candidates
        .map(
            (candidate) => `
        <tr>
            <td>${candidate.name}</td>
            <td>${candidate.position}</td>
            <td>${candidate.pipeline_stage}</td>
            <td>${candidate.action_required}</td>
            <td>${candidate.priority}</td>
            <td>${formatDateTime(candidate.next_interview_datetime)}</td>
            <td>${formatDate(candidate.expected_joining_date)}</td>
            <td>${shortenNotes(candidate.notes)}</td>
        </tr>
    `,
        )
        .join("");

    return `
    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Position</th>
                    <th>Stage</th>
                    <th>Action</th>
                    <th>Priority</th>
                    <th>Next Interview</th>
                    <th>Joining</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    </div>
    `;
}

async function loadActionItems() {
    const actionItems = await apiRequest("/api/action-items");
    const groups = ["SCHEDULE", "RESCHEDULE", "DECIDE", "FOLLOW_UP"];
    const container = document.getElementById("action-items-content");

    container.innerHTML = groups
        .map((group) => {
            const candidates = actionItems.filter((item) => item.action_required === group);
            return `<section><h3>${group}</h3>${renderSimpleTable(candidates)}</section>`;
        })
        .join("");
}

async function loadCalendar() {
    const windowValue = document.getElementById("calendar-window").value;
    const includeJoining = document.getElementById("include-joining").checked;
    const payload = await apiRequest(`/api/calendar?window=${windowValue}&include_joining=${includeJoining}`);

    document.getElementById("calendar-interviews").innerHTML = renderSimpleTable(payload.interviews);
    document.getElementById("calendar-joinings").innerHTML = renderSimpleTable(payload.joinings);
}

async function loadCandidateDetail(candidateId) {
    const candidate = await apiRequest(`/api/candidates/${candidateId}`);
    state.selectedCandidateId = candidateId;

    document.getElementById("detail-form").classList.remove("hidden");
    document.getElementById("detail-hint").classList.add("hidden");

    document.getElementById("detail-id").value = candidate.id;
    document.getElementById("detail-name").value = candidate.name;
    document.getElementById("detail-position").value = candidate.position;
    document.getElementById("detail-stage").value = candidate.pipeline_stage;
    document.getElementById("detail-action").value = candidate.action_required;
    document.getElementById("detail-priority").value = candidate.priority;
    document.getElementById("detail-round").value = candidate.current_round || "";
    document.getElementById("detail-next-interview").value = toDateTimeLocal(candidate.next_interview_datetime);
    document.getElementById("detail-joining-date").value = candidate.expected_joining_date || "";
    document.getElementById("detail-notes").value = candidate.notes || "";
    document.getElementById("detail-created").textContent = formatDateTime(candidate.created_at);
    document.getElementById("detail-updated").textContent = formatDateTime(candidate.updated_at);
}

async function refreshAllViews() {
    await loadMetadata();
    await Promise.all([loadCandidates(), loadActionItems(), loadCalendar()]);
}

function switchView(viewId) {
    document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
    document.querySelectorAll(".tab-button").forEach((button) => button.classList.remove("active"));

    document.getElementById(viewId).classList.add("active");
    document.querySelector(`.tab-button[data-view="${viewId}"]`).classList.add("active");
}

function bindEvents() {
    document.getElementById("add-candidate-form").addEventListener("submit", async (event) => {
        event.preventDefault();

        const name = document.getElementById("new-name").value.trim();
        const position = document.getElementById("new-position").value.trim();
        const priority = document.getElementById("new-priority").value;
        const notes = document.getElementById("new-notes").value.trim();

        if (!name || !position) {
            setStatus("Name and position are required", true);
            return;
        }

        try {
            await apiRequest("/api/candidates", {
                method: "POST",
                body: JSON.stringify({ name, position, priority, notes }),
            });
            event.target.reset();
            document.getElementById("new-priority").value = "MEDIUM";
            setStatus("Candidate added");
            await refreshAllViews();
        } catch (error) {
            setStatus(error.message, true);
        }
    });

    document.getElementById("filters").addEventListener("change", async () => {
        try {
            await loadCandidates();
        } catch (error) {
            setStatus(error.message, true);
        }
    });

    document.getElementById("calendar-controls").addEventListener("change", async () => {
        try {
            await loadCalendar();
        } catch (error) {
            setStatus(error.message, true);
        }
    });

    document.querySelectorAll(".tab-button").forEach((button) => {
        button.addEventListener("click", () => {
            switchView(button.dataset.view);
        });
    });

    document.getElementById("detail-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const candidateId = Number(document.getElementById("detail-id").value);

        const payload = {
            name: document.getElementById("detail-name").value.trim(),
            position: document.getElementById("detail-position").value.trim(),
            pipeline_stage: document.getElementById("detail-stage").value,
            action_required: document.getElementById("detail-action").value,
            priority: document.getElementById("detail-priority").value,
            current_round: document.getElementById("detail-round").value.trim() || null,
            next_interview_datetime: document.getElementById("detail-next-interview").value || null,
            expected_joining_date: document.getElementById("detail-joining-date").value || null,
            notes: document.getElementById("detail-notes").value.trim(),
        };

        if (!payload.name || !payload.position) {
            setStatus("Name and position are required", true);
            return;
        }

        try {
            await apiRequest(`/api/candidates/${candidateId}`, {
                method: "PATCH",
                body: JSON.stringify(payload),
            });
            setStatus("Candidate details saved");
            await Promise.all([refreshAllViews(), loadCandidateDetail(candidateId)]);
        } catch (error) {
            setStatus(error.message, true);
        }
    });

    document.getElementById("delete-candidate").addEventListener("click", async () => {
        const candidateId = Number(document.getElementById("detail-id").value);
        if (!candidateId) return;

        const confirmed = window.confirm("Delete this candidate? This cannot be undone.");
        if (!confirmed) return;

        try {
            await apiRequest(`/api/candidates/${candidateId}`, { method: "DELETE" });
            setStatus("Candidate deleted");
            state.selectedCandidateId = null;
            document.getElementById("detail-form").classList.add("hidden");
            document.getElementById("detail-hint").classList.remove("hidden");
            await refreshAllViews();
        } catch (error) {
            setStatus(error.message, true);
        }
    });
}

async function init() {
    try {
        await loadMetadata();
        bindEvents();
        await Promise.all([loadCandidates(), loadActionItems(), loadCalendar()]);
        document.getElementById("new-priority").value = "MEDIUM";
        setStatus("Ready");
    } catch (error) {
        setStatus(error.message, true);
    }
}

init();
