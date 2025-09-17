import { CONFIG } from "../config.js";
import { getToken } from "./auth.js";

async function request(path, { method = "GET", body = null, auth = false } = {}) {
    const headers = {};
    if (body) headers["Content-Type"] = "application/json";
    if (auth) {
        const token = await getToken();
        console.log("Firebase ID Token:", token);
        if (token) headers["Authorization"] = "Bearer " + token;
    }
    const res = await fetch(CONFIG.API_BASE + path, {
        method, headers, body: body ? JSON.stringify(body) : null
    });
    if (!res.ok) {
        let msg;
        try { msg = (await res.json()).message || res.statusText; } catch { msg = res.statusText; }
        const err = new Error(msg);
        err.status = res.status;
        throw err;
    }
    const ct = res.headers.get("Content-Type") || "";
    if (ct.includes("application/json")) return res.json();
    return res.text();
}

export const api = {
    health: () => request("/health"),
    me: () => request("/api/me", { auth: true }),
    listEvents: () => request("/api/events"),
    createEvent: (data) => request("/api/events", { method: "POST", body: data, auth: true }),
    approveEvent: (id) => request(`/api/events/${id}/approve`, { method: "POST", auth: true }),
    register: (id) => request(`/api/events/${id}/register`, { method: "POST", auth: true }),
    cancel: (id) => request(`/api/events/${id}/register`, { method: "DELETE", auth: true }),
    allIcsUrl: () => CONFIG.API_BASE + "/api/events.ics",
    singleIcsUrl: (id) => CONFIG.API_BASE + `/api/events/${id}.ics`
};