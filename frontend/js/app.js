import { login, logout, onUserChanged, getUser } from "./auth.js";
import { api } from "./api.js";
import { refreshEvents } from "./events.js";
import { toggleCreateForm, showUserInfo } from "./ui.js";
import { isoFromLocalInput } from "./time.js";
import { getAuth } from "firebase/auth";

const auth = getAuth();

const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const createForm = document.getElementById("createForm");
const cancelCreate = document.getElementById("cancelCreate");
const createError = document.getElementById("createError");

loginBtn.onclick = async () => {
    console.log("Login button clicked")
    loginBtn.disabled = true;
    try { await login(); } catch (e) { showToast("Login failed: " + e.message, true); }
    finally { loginBtn.disabled = false; }
};

logoutBtn.onclick = async () => {
    await logout();
};

cancelCreate.onclick = () => {
    toggleCreateForm(false);
};

document.addEventListener("click", (e) => {
    // Quick way to open form (admin/organizer) – you might add separate button logic
    if (e.target.id === "openCreate") {
        toggleCreateForm(true);
    }
});

createForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    createError.style.display = "none";
    const fd = new FormData(createForm);
    const data = {
        title: fd.get("title").trim(),
        startTime: isoFromLocalInput(fd.get("startTime")),
        endTime: isoFromLocalInput(fd.get("endTime")),
        capacity: parseInt(fd.get("capacity"), 10),
        description: fd.get("description").trim()
    };
    if (!data.title || !data.startTime || !data.endTime || !data.capacity) {
        createError.textContent = "All fields (except description) required.";
        createError.style.display = "block";
        return;
    }
    if (new Date(data.startTime) >= new Date(data.endTime)) {
        createError.textContent = "End time must be after start time.";
        createError.style.display = "block";
        return;
    }
    try {
        const ev = await api.createEvent(data);
        showToast("Event created (pending)");
        createForm.reset();
        toggleCreateForm(false);
        // Pending won't show unless your backend returns them in /api/events for admin
        const meData = window.__ME_DATA__;
        await refreshEvents(meData);
    } catch (err) {
        createError.textContent = err.message;
        createError.style.display = "block";
    }
});

if (auth.currentUser) {
    auth.currentUser.getIdToken(true)
        .then((token) => {
            console.log("Your ID Token:", token);
        });
}

// Provide global toast
export function showToast(msg, error = false) {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.style.borderColor = error ? "var(--danger)" : "var(--border)";
    t.classList.remove("hidden");
    setTimeout(() => t.classList.add("show"), 10);
    setTimeout(() => {
        t.classList.remove("show");
        setTimeout(() => t.classList.add("hidden"), 250);
    }, 3000);
}

// Handle auth state
onUserChanged(async (user, token) => {
    const loginBtn = document.getElementById("loginBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    if (user) {
        loginBtn.style.display = "none";
        logoutBtn.style.display = "inline-block";
        await loadMe();
    } else {
        loginBtn.style.display = "inline-block";
        logoutBtn.style.display = "none";
        window.__ME_DATA__ = null;
        showUserInfo(null);
        await refreshEvents(null);
    }
});

// Load /api/me
async function loadMe() {
    try {
        const me = await api.me();
        window.__ME_DATA__ = me;
        showUserInfo(me);
        // Show create panel trigger if role qualifies
        if (me.roles.includes("admin") || me.roles.includes("organizer")) {
            // You could show a button to open the form
            // For now, auto-show create if none existing
            // toggleCreateForm(true); (optional – comment out if you prefer a manual button)
        }
        await refreshEvents(me);
    } catch (err) {
        showToast("Failed /api/me: " + err.message, true);
        window.__ME_DATA__ = null;
        showUserInfo(null);
    }
}

// Initial health check & events (unauthenticated)
(async function init() {
    try { await api.health(); } catch (e) { showToast("Backend unreachable: " + e.message, true); }
    await refreshEvents(null);
})();