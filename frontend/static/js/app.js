
"use strict";

// ------------------------------
// DOM ELEMENTS
// ------------------------------

const loginForm = document.getElementById("login-form");
const transferForm = document.getElementById("transfer-form");

const loginMessage = document.getElementById("login-message");
const transferMessage = document.getElementById("transfer-message");

const loginCard = document.getElementById("login-card");
const transferCard = document.getElementById("transfer-card");
const historyCard = document.getElementById("history-card");

const historyContainer = document.getElementById("history");
const refreshButton = document.getElementById("refresh-button");

// ------------------------------
// HELPER FUNCTIONS
// ------------------------------

function showMessage(element, message, success = true) {
    element.textContent = message;
    element.classList.remove("success", "error");
    element.classList.add(success ? "success" : "error");
}

async function readJsonResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || `Request failed: ${response.status}`);
    }

    return data;
}

// ------------------------------
// LOGIN
// ------------------------------

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const submitButton = loginForm.querySelector("button");

    submitButton.disabled = true;
    showMessage(loginMessage, "Logging in...", true);

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const result = await readJsonResponse(response);

        showMessage(loginMessage, result.message, result.success);

        if (result.success) {
            loginCard.classList.add("hidden");
            transferCard.classList.remove("hidden");
            historyCard.classList.remove("hidden");

            await loadHistory();
        }

    } catch (error) {
        console.error("Login error:", error);

        showMessage(
            loginMessage,
            error.message || "Unable to connect to the backend.",
            false
        );

    } finally {
        submitButton.disabled = false;
    }
});

// ------------------------------
// FILE TRANSFER
// ------------------------------

transferForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const sender = document.getElementById("sender").value.trim();
    const receiver = document.getElementById("receiver").value.trim();
    const fileInput = document.getElementById("file");

    const file = fileInput.files[0];

    if (!file) {
        showMessage(transferMessage, "Please select a file.", false);
        return;
    }

    if (!sender || !receiver) {
        showMessage(
            transferMessage,
            "Sender and receiver are required.",
            false
        );
        return;
    }

    const formData = new FormData();

    formData.append("sender", sender);
    formData.append("receiver", receiver);
    formData.append("file", file);

    const submitButton = transferForm.querySelector("button");

    submitButton.disabled = true;
    showMessage(
        transferMessage,
        "Encrypting and transferring file...",
        true
    );

    try {
        const response = await fetch("/api/transfer", {
            method: "POST",
            body: formData
        });

        const result = await readJsonResponse(response);

        showMessage(
            transferMessage,
            result.message || "Transfer completed.",
            result.success
        );

        if (result.success) {
            let details = "";

            if (result.transfer_id !== undefined) {
                details += ` Transfer ID: ${result.transfer_id}.`;
            }

            if (result.risk && result.risk.risk_label) {
                details += ` Risk: ${result.risk.risk_label}.`;
            }

            showMessage(
                transferMessage,
                (result.message || "Transfer completed.") + details,
                true
            );

            transferForm.reset();

            document.getElementById("sender").value = "Organization A";
            document.getElementById("receiver").value = "Organization B";

            await loadHistory();
        }

    } catch (error) {
        console.error("Transfer error:", error);

        showMessage(
            transferMessage,
            error.message || "Unable to complete the transfer.",
            false
        );

    } finally {
        submitButton.disabled = false;
    }
});

// ------------------------------
// TRANSFER HISTORY
// ------------------------------

refreshButton.addEventListener("click", loadHistory);

async function loadHistory() {
    historyContainer.textContent = "Loading transfer history...";
    refreshButton.disabled = true;

    try {
        const response = await fetch("/api/transfers");
        const transfers = await readJsonResponse(response);

        if (!Array.isArray(transfers) || transfers.length === 0) {
            historyContainer.textContent = "No transfers recorded yet.";
            return;
        }

        renderHistory(transfers);

    } catch (error) {
        console.error("History error:", error);

        historyContainer.textContent =
            error.message || "Unable to load transfer history.";

    } finally {
        refreshButton.disabled = false;
    }
}

// ------------------------------
// RENDER HISTORY SAFELY
// ------------------------------

function renderHistory(transfers) {
    historyContainer.replaceChildren();

    transfers.forEach((item) => {
        const row = document.createElement("div");
        row.className = "transfer-row";

        const filename = document.createElement("strong");
        filename.textContent = item.original_filename || "Unknown file";

        const organizations = document.createElement("div");
        organizations.textContent =
            `${item.sender || "Unknown"} → ${item.receiver || "Unknown"}`;

        const details = document.createElement("small");
        details.textContent =
            `Size: ${item.file_size ?? "Unknown"} bytes | ` +
            `Risk: ${item.risk_label || "Unknown"} | ` +
            `Created: ${item.created_at || "Unknown"}`;

        row.append(filename, organizations, details);
        historyContainer.appendChild(row);
    });
}