export function formatDate(dtIso) {
    try {
        const d = new Date(dtIso);
        return d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
    } catch {
        return dtIso;
    }
}

export function isoFromLocalInput(localValue) {
    // localValue from <input type="datetime-local">
    if (!localValue) return null;
    // Treat as local time, convert to UTC ISO with Z
    const d = new Date(localValue);
    return d.toISOString().replace(/\.\d{3}Z$/, "Z");
}

export function isRecent(createdAt, hours = 24) {
    try {
        return (Date.now() - new Date(createdAt).getTime()) < hours * 3600 * 1000;
    } catch { return false; }
}