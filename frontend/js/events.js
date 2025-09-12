import { api } from "./api.js";
import { renderEvents, renderPending, setAllIcsLink } from "./ui.js";
import { showToast } from "./app.js";

export async function refreshEvents(userData) {
    const loading = document.getElementById("eventsLoading");
    loading.style.display = "block";
    try {
        const list = await api.listEvents();
        // Split approved vs pending: backend only returns approved (per earlier design),
        // If you want pending you’d need a separate endpoint or modify backend to include or provide admin list.
        // For hackathon: We’ll assume you added logic: return all if admin? If not, this section can be dummy.
        const approved = list.filter(e => e.status === "approved" || e.status === "approved"); // redundant but placeholder
        const pending = list.filter(e => e.status === "pending");
        renderEvents(approved, userData, {
            onRegister: async (id) => { await api.register(id); showToast("Registered"); await refreshEvents(userData); },
            onCancel: async (id) => { await api.cancel(id); showToast("Canceled"); await refreshEvents(userData); },
            onApprove: async () => { } // not used here
        });
        renderPending(pending, userData, {
            onApprove: async (id) => {
                await api.approveEvent(id);
                showToast("Approved");
                await refreshEvents(userData);
            }
        });
        setAllIcsLink(api.allIcsUrl());
    } catch (e) {
        showToast("Failed to load events: " + e.message, true);
    } finally {
        loading.style.display = "none";
    }
}