// Error message extraction from API responses
export function getErrorMessage(error) {
    if (typeof error.detail === "string") {
        return error.detail;
    } else if (Array.isArray(error.detail)) {
        return error.detail.map((err) => err.msg).join(". ");
    }
    return "An error occurred. Please try again.";
}

// Show a Bootstrap modal by ID
export function showModal(modalId) {
    const modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById(modalId),
    );
    modal.show();
    return modal;
}

// Hide a Bootstrap modal by ID
export function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) modal.hide();
}

// XSS prevention for dynamic content insertion
export function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Date formatting to match server's strftime("%B %d, %Y")
export function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "2-digit",
    });
}