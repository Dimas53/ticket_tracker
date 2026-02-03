const API_BASE = "http://127.0.0.1:8001";
let tickets = [];
let selectedId = null;

async function fetchTickets() {
    try {
        const res = await fetch(`${API_BASE}/tickets`);
        if (!res.ok) {
            throw new Error(`Failed to load tickets: ${res.status}`);
        }
        tickets = await res.json();
        renderAll();
    } catch (err) {
        showAlert(err.message || "Error while loading tickets");
    }
}

function renderAll() {
    renderSummary();
    renderCards();
    renderTable();
    renderDetailForm();
}

function renderSummary() {
    const el = document.getElementById("summaryText");
    if (!tickets.length) {
        el.textContent = "No tickets yet.";
        return;
    }
    const open = tickets.filter(t => t.status === "open").length;
    const inProgress = tickets.filter(t => t.status === "in_progress").length;
    const done = tickets.filter(t => t.status === "done").length;
    el.textContent = `${tickets.length} tickets · open: ${open}, in progress: ${inProgress}, done: ${done}`;
}

function renderCards() {
    const container = document.getElementById("ticketCards");
    container.innerHTML = "";

    if (!tickets.length) {
        const emptyCard = document.createElement("div");
        emptyCard.className = "ticket-card";
        emptyCard.innerHTML = "<div class='ticket-card-title'>No tickets yet</div><div class='ticket-card-id'>Create your first ticket on the right.</div>";
        container.appendChild(emptyCard);
        return;
    }

    const sorted = [...tickets].sort((a, b) => b.id - a.id);
    const top = sorted.slice(0, 6);

    top.forEach(ticket => {
        const card = document.createElement("div");
        card.className = "ticket-card" + (ticket.id === selectedId ? " selected" : "");
        card.onclick = () => selectTicket(ticket.id);

        const title = document.createElement("div");
        title.className = "ticket-card-title";
        title.textContent = ticket.title;

        const idLine = document.createElement("div");
        idLine.className = "ticket-card-id";
        idLine.textContent = `#${ticket.id} · ${ticket.assignee}`;

        const badges = document.createElement("div");
        badges.className = "badge-row";
        badges.innerHTML = `
            <span class="badge badge-status-${ticket.status}">${ticket.status}</span>
            <span class="badge badge-priority-${ticket.priority}">${ticket.priority}</span>
        `;

        card.appendChild(title);
        card.appendChild(idLine);
        card.appendChild(badges);

        container.appendChild(card);
    });
}

function renderTable() {
    const body = document.getElementById("ticketTableBody");
    body.innerHTML = "";

    tickets
        .slice()
        .sort((a, b) => a.id - b.id)
        .forEach(ticket => {
            const tr = document.createElement("tr");
            if (ticket.id === selectedId) {
                tr.classList.add("selected");
            }
            tr.onclick = () => selectTicket(ticket.id);

            tr.innerHTML = `
                <td>${ticket.id}</td>
                <td>${escapeHtml(ticket.title)}</td>
                <td>${escapeHtml(ticket.assignee)}</td>
                <td class="status-cell">
                    <span class="badge badge-status-${ticket.status}">${ticket.status}</span>
                </td>
                <td>
                    <span class="badge badge-priority-${ticket.priority}">${ticket.priority}</span>
                </td>
                <td class="description-cell" title="${escapeHtml(ticket.description)}">
                    ${escapeHtml(ticket.description)}
                </td>
            `;
            body.appendChild(tr);
        });
}

function renderDetailForm() {
    const titleEl = document.getElementById("detailTitle");
    const metaEl = document.getElementById("detailMeta");
    const idInput = document.getElementById("ticketId");
    const titleInput = document.getElementById("title");
    const descInput = document.getElementById("description");
    const assigneeInput = document.getElementById("assignee");
    const statusSelect = document.getElementById("status");
    const prioritySelect = document.getElementById("priority");
    const deleteBtn = document.getElementById("deleteTicketBtn");

    const ticket = tickets.find(t => t.id === selectedId);
    if (!ticket) {
        titleEl.textContent = "Create new ticket";
        metaEl.textContent = "Fill the form and click Save to create a ticket.";
        const nextId = getNextId();
        idInput.value = nextId;
        titleInput.value = "";
        descInput.value = "";
        assigneeInput.value = "";
        statusSelect.value = "open";
        prioritySelect.value = "normal";
        deleteBtn.disabled = true;
        return;
    }

    titleEl.textContent = `Ticket #${ticket.id}`;
    metaEl.textContent = `Editing ticket assigned to ${ticket.assignee}.`;
    idInput.value = ticket.id;
    titleInput.value = ticket.title;
    descInput.value = ticket.description;
    assigneeInput.value = ticket.assignee;
    statusSelect.value = ticket.status;
    prioritySelect.value = ticket.priority;
    deleteBtn.disabled = false;
}

function selectTicket(id) {
    selectedId = id;
    clearAlert();
    renderAll();
}

function getNextId() {
    if (!tickets.length) return 1;
    return Math.max(...tickets.map(t => t.id)) + 1;
}

async function saveTicket(event) {
    event.preventDefault();
    clearAlert();

    const id = parseInt(document.getElementById("ticketId").value, 10);
    const ticketPayload = {
        id,
        title: document.getElementById("title").value.trim(),
        description: document.getElementById("description").value.trim(),
        assignee: document.getElementById("assignee").value.trim(),
        status: document.getElementById("status").value,
        priority: document.getElementById("priority").value
    };

    if (!ticketPayload.title || !ticketPayload.description || !ticketPayload.assignee) {
        showAlert("Please fill all required fields.");
        return;
    }

    const existing = tickets.find(t => t.id === id);
    const url = existing
        ? `${API_BASE}/tickets/${id}`
        : `${API_BASE}/tickets`;
    const method = existing ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(ticketPayload)
        });

        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            const msg = data.detail || `Request failed with status ${res.status}`;
            throw new Error(msg);
        }

        await fetchTickets();
        selectedId = id;
        showAlert(existing ? "Ticket updated." : "Ticket created.", false);
    } catch (err) {
        showAlert(err.message || "Error while saving ticket");
    }
}

async function deleteSelectedTicket() {
    clearAlert();
    if (selectedId == null) {
        showAlert("No ticket selected.");
        return;
    }

    if (!confirm(`Delete ticket #${selectedId}?`)) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/tickets/${selectedId}`, {
            method: "DELETE"
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            const msg = data.detail || `Delete failed with status ${res.status}`;
            throw new Error(msg);
        }
        selectedId = null;
        await fetchTickets();
        showAlert("Ticket deleted.", false);
    } catch (err) {
        showAlert(err.message || "Error while deleting ticket");
    }
}

/*function resetForm() {
    clearAlert();
    selectedId = null;
    renderDetailForm();
    renderCards();
    renderTable();
}*/

function resetForm() {
    clearAlert();
    selectedId = null;

    // Очищаем форму и рендерим пустые поля
    renderDetailForm();
    renderCards();
    renderTable();

    // Добавляем эффект подсветки для правой колонки (формы)
    const detailCard = document.querySelector('.detail-column .card');
    if (detailCard) {
        // Убираем класс, если он уже был (чтобы можно было кликать несколько раз)
        detailCard.classList.remove('highlight-flash');

        // Маленький трюк, чтобы браузер "заметил" удаление и добавил класс заново
        void detailCard.offsetWidth;

        detailCard.classList.add('highlight-flash');
    }
}

function showAlert(message, isError = true) {
    const box = document.getElementById("alertBox");
    box.style.display = "block";
    box.textContent = message;
    box.style.background = isError ? "#fef3c7" : "#dcfce7";
    box.style.color = isError ? "#92400e" : "#166534";
}

function clearAlert() {
    const box = document.getElementById("alertBox");
    box.style.display = "none";
    box.textContent = "";
}

function escapeHtml(str) {
    if (typeof str !== "string") return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("ticketForm").addEventListener("submit", saveTicket);
    document.getElementById("deleteTicketBtn").addEventListener("click", deleteSelectedTicket);
//    document.getElementById("refreshBtn").addEventListener("click", fetchTickets);
    document.getElementById("resetBtn").addEventListener("click", resetForm);
    document.getElementById("newTicketBtn").addEventListener("click", resetForm);


    // НОВЫЙ БЛОК:
    const themeBtn = document.getElementById("themeToggle");
    const body = document.body;

    // Проверяем сохраненную тему
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-theme");
        themeBtn.textContent = "☀️";
    }

    themeBtn.onclick = () => {
        body.classList.toggle("dark-theme");
        const isDark = body.classList.contains("dark-theme");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        themeBtn.textContent = isDark ? "☀️" : "🌕";
    };

    fetchTickets();
});

function updateThemeUI(isDark) {
    const themeBtn = document.getElementById("themeToggle");
    // Если тема темная — показываем солнце, если светлая — луну
    themeBtn.textContent = isDark ? "☀️" : "🌕";
}