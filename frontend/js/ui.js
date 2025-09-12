import { formatDate, isRecent } from "./time.js";
import { api } from "./api.js";
import { showToast } from "./app.js";

export function renderEvents(approved, user, { onRegister, onCancel, onApprove }) {
    const list = document.getElementById("eventsList");
    const empty = document.getElementById("eventsEmpty");
    list.innerHTML = "";
    if (approved.length === 0) {
        empty.classList.remove("hidden");
        return;
    }
    empty.classList.add("hidden");

    approved.forEach(e => {
        const li = document.createElement("li");
        li.className = "event";

        const title = document.createElement("div");
        title.className = "title";
        title.textContent = e.title;

        if (isRecent(e.createdAt)) {
            const badge = document.createElement("span");
            badge.className = "badge";
            badge.textContent = "NEW";
            title.appendChild(badge);
        }

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.innerHTML = `
      <span>${formatDate(e.startTime)} → ${formatDate(e.endTime)}</span>
      <span>${e.registeredCount}/${e.capacity} spots</span>
      <span>Status: ${e.status}</span>
    `;

        const desc = document.createElement("div");
        desc.className = "desc";
        desc.textContent = e.description || "";

        const actions = document.createElement("div");
        actions.className = "actions";

        // Register / Cancel
        if (user) {
            const regBtn = document.createElement("button");
            regBtn.className = "btn small primary";
            regBtn.textContent = "Register";
            regBtn.onclick = async () => {
                regBtn.disabled = true;
                try { await onRegister(e.id); } catch (err) { showToast(err.message, true); } finally { regBtn.disabled = false; }
            };
            actions.appendChild(regBtn);

            const cancelBtn = document.createElement("button");
            cancelBtn.className = "btn small";
            cancelBtn.textContent = "Cancel";
            cancelBtn.onclick = async () => {
                cancelBtn.disabled = true;
                try { await onCancel(e.id); } catch (err) { showToast(err.message, true); } finally { cancelBtn.disabled = false; }
            };
            actions.appendChild(cancelBtn);
        }

        // Approve button not shown here (approved list), appears in pending list instead.

        // ICS download link
        const icsLink = document.createElement("a");
        icsLink.href = api.singleIcsUrl(e.id);
        icsLink.className = "link";
        icsLink.textContent = "ICS";
        icsLink.setAttribute("download", `${e.title}.ics`);
        actions.appendChild(icsLink);

        li.appendChild(title);
        li.appendChild(meta);
        if (e.description) li.appendChild(desc);
        li.appendChild(actions);
        list.appendChild(li);
    });
}

export function renderPending(pending, user, { onApprove }) {
    const wrap = document.getElementById("pendingSection");
    const list = document.getElementById("pendingList");
    const empty = document.getElementById("pendingEmpty");
    if (!user || !user.roles?.includes("admin")) {
        wrap.classList.add("hidden");
        return;
    }
    wrap.classList.remove("hidden");
    list.innerHTML = "";
    if (pending.length === 0) {
        empty.classList.remove("hidden");
        return;
    }
    empty.classList.add("hidden");

    pending.forEach(e => {
        const li = document.createElement("li");
        li.className = "event";
        li.innerHTML = `
      <div class="title">${e.title}</div>
      <div class="meta">
        <span>${formatDate(e.startTime)} → ${formatDate(e.endTime)}</span>
        <span>Pending</span>
      </div>
    `;
        const actions = document.createElement("div");
        actions.className = "actions";
        const approveBtn = document.createElement("button");
        approveBtn.className = "btn small primary";
        approveBtn.textContent = "Approve";
        approveBtn.onclick = async () => {
            approveBtn.disabled = true;
            try { await onApprove(e.id); } catch (err) { showToast(err.message, true); } finally { approveBtn.disabled = false; }
        };
        actions.appendChild(approveBtn);
        li.appendChild(actions);
        list.appendChild(li);
    });
}

export function setAllIcsLink(url) {
    document.getElementById("allIcsLink").href = url;
}

export function toggleCreateForm(show) {
    const section = document.getElementById("createSection");
    if (show) section.classList.remove("hidden");
    else section.classList.add("hidden");
}

export function showUserInfo(userData) {
    const el = document.getElementById("userInfo");
    if (!userData) {
        el.classList.add("hidden");
        el.innerHTML = "";
        return;
    }
    el.classList.remove("hidden");
    el.innerHTML = `
    <h2>User</h2>
    <p>${userData.email} • Roles: ${(userData.roles || []).join(", ") || "user"}</p>
  `;
}