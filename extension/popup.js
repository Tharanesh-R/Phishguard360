// =============================
// CONFIGURATION
// =============================

const BACKEND_URL = "http://127.0.0.1:5000";
const AUTO_SCAN_KEY = "cybershield_auto_scan";
const AUTO_BLOCK_KEY = "cybershield_auto_block";
const PROTECTION_LEVEL_KEY = "cybershield_protection_level";
const BLOCKED_LOG_KEY = "cybershield_blocked_log";
const BLOCK_COUNT_KEY = "cybershield_block_count_today";
const BLOCK_COUNT_DATE_KEY = "cybershield_block_count_date";

// =============================
// DOM ELEMENTS
// =============================

const scanBtn = document.getElementById("scanBtn");
const resultBox = document.getElementById("resultBox");
const riskLabel = document.getElementById("riskLabel");
const riskScore = document.getElementById("riskScore");
const riskMessage = document.getElementById("riskMessage");
const urlDisplay = document.getElementById("urlDisplay");
const autoScanToggle = document.getElementById("autoScanToggle");
const autoBlockToggle = document.getElementById("autoBlockToggle");
const protectionLevel = document.getElementById("protectionLevel");
const statusIndicator = document.getElementById("statusIndicator");
const backendStatus = document.getElementById("backendStatus");
const domainDisplay = document.getElementById("domainDisplay");
const trustBadge = document.getElementById("trustBadge");
const flagsContainer = document.getElementById("flagsContainer");
const flagsList = document.getElementById("flagsList");
const modelBadge = document.getElementById("modelBadge");
const threatCounter = document.getElementById("threatCounter");
const threatCount = document.getElementById("threatCount");
const threatSubtext = document.getElementById("threatSubtext");
const recentBlocksHeader = document.getElementById("recentBlocksHeader");
const recentBlocksList = document.getElementById("recentBlocksList");
const recentBlocksCount = document.getElementById("recentBlocksCount");

// =============================
// STATE
// =============================

let currentUrl = "";
let isScanning = false;

// =============================
// INITIALIZE
// =============================

async function initialize() {
    // Load preferences
    chrome.storage.sync.get([AUTO_SCAN_KEY, AUTO_BLOCK_KEY, PROTECTION_LEVEL_KEY], (result) => {
        autoScanToggle.checked = result[AUTO_SCAN_KEY] !== false;
        autoBlockToggle.checked = result[AUTO_BLOCK_KEY] !== false;
        protectionLevel.value = result[PROTECTION_LEVEL_KEY] || "standard";
    });

    // Load threat counter
    loadThreatCounter();

    // Load recent blocks
    loadRecentBlocks();

    // Check backend
    await checkBackendStatus();

    // Get current tab URL
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
            currentUrl = tab.url;
            urlDisplay.textContent = currentUrl;

            // Auto-scan if enabled
            chrome.storage.sync.get([AUTO_SCAN_KEY], (result) => {
                if (result[AUTO_SCAN_KEY] !== false) {
                    scanWebsite();
                }
            });
        } else {
            urlDisplay.textContent = "Unable to get current URL";
        }
    } catch (error) {
        console.error("Error getting tab:", error);
        urlDisplay.textContent = "Error loading URL";
    }
}

// =============================
// THREAT COUNTER
// =============================

function loadThreatCounter() {
    const today = new Date().toISOString().slice(0, 10);
    chrome.storage.local.get([BLOCK_COUNT_KEY, BLOCK_COUNT_DATE_KEY], (result) => {
        let count = 0;
        if (result[BLOCK_COUNT_DATE_KEY] === today) {
            count = result[BLOCK_COUNT_KEY] || 0;
        }
        threatCount.textContent = count;
        if (count > 0) {
            threatCounter.className = "threat-counter";
            threatSubtext.textContent = `CyberShield is actively protecting you`;
        } else {
            threatCounter.className = "threat-counter safe";
            threatSubtext.textContent = "Your browsing is protected";
        }
    });
}

// =============================
// RECENT BLOCKS
// =============================

function loadRecentBlocks() {
    chrome.storage.local.get([BLOCKED_LOG_KEY], (result) => {
        const log = result[BLOCKED_LOG_KEY] || [];
        const recent = log.slice(0, 5);

        if (recent.length > 0) {
            recentBlocksCount.textContent = `(${log.length})`;
        } else {
            recentBlocksCount.textContent = "";
        }

        recentBlocksList.innerHTML = "";

        if (recent.length === 0) {
            recentBlocksList.innerHTML = '<div class="no-blocks-msg">No threats blocked yet — you\'re safe! 🎉</div>';
            return;
        }

        recent.forEach((entry) => {
            const catIcons = {
                "Phishing": "🎣", "Malware": "🦠", "Scam": "💰",
                "Cryptomining": "⛏️", "Command & Control": "🖥️",
                "Suspicious": "⚠️", "Caution": "🔶"
            };
            const icon = catIcons[entry.category] || "⛔";
            const time = formatTimeAgo(entry.timestamp);

            const div = document.createElement("div");
            div.className = "block-entry";
            div.innerHTML = `
                <span class="block-entry-icon">${icon}</span>
                <div class="block-entry-info">
                    <div class="block-entry-domain">${escapeHtml(entry.domain || "unknown")}</div>
                    <div class="block-entry-meta">
                        <span>${entry.category || "Threat"}</span>
                        <span>•</span>
                        <span>${time}</span>
                    </div>
                </div>
                <div class="block-entry-risk">${Math.round(entry.risk_score)}%</div>
            `;
            recentBlocksList.appendChild(div);
        });
    });
}

function formatTimeAgo(timestamp) {
    try {
        const now = new Date();
        const then = new Date(timestamp);
        const diffMs = now - then;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 1) return "just now";
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return then.toLocaleDateString();
    } catch { return "recently"; }
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// =============================
// BACKEND STATUS CHECK
// =============================

async function checkBackendStatus() {
    try {
        const response = await fetch(`${BACKEND_URL}/test`, {
            method: "GET",
            signal: AbortSignal.timeout(3000)
        });

        if (response.ok) {
            statusIndicator.className = "status-dot status-online";
            backendStatus.textContent = "Backend Online";

            // Fetch model info
            try {
                const modelRes = await fetch(`${BACKEND_URL}/api/model_info`, {
                    signal: AbortSignal.timeout(3000)
                });
                if (modelRes.ok) {
                    const info = await modelRes.json();
                    if (info.accuracy) {
                        modelBadge.innerHTML = `🧠 <strong>${info.model_name || info.model_type}</strong> — ${info.accuracy}%`;
                    }
                }
            } catch (e) { /* ignore */ }

            return true;
        } else {
            throw new Error("Backend not responding");
        }
    } catch (error) {
        statusIndicator.className = "status-dot status-offline";
        backendStatus.textContent = "Backend Offline";
        return false;
    }
}

// =============================
// SCAN WEBSITE
// =============================

async function scanWebsite() {
    if (isScanning) return;

    isScanning = true;
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;margin:0;"></div> Scanning...';

    resultBox.className = "result-box result-scanning show";
    domainDisplay.textContent = "";
    riskLabel.textContent = "Analyzing URL...";
    riskScore.innerHTML = '<div class="spinner"></div>';
    riskMessage.textContent = "Checking against threat database & AI model";
    trustBadge.innerHTML = "";
    flagsContainer.className = "flags-section";
    flagsList.innerHTML = "";

    try {
        const response = await fetch(`${BACKEND_URL}/api/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: currentUrl })
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        displayResult(data);

    } catch (error) {
        console.error("Scan error:", error);
        showError("Unable to connect to backend. Please ensure Flask server is running on port 5000.");
    } finally {
        isScanning = false;
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Scan This Website';
    }
}

// =============================
// DISPLAY RESULT
// =============================

function displayResult(data) {
    const score = data.risk_score;
    const label = data.label;
    const trust = data.trust_status || "unknown";
    const domain = data.domain || "";
    const flags = data.flags || [];

    if (domain) {
        domainDisplay.textContent = `🌐 ${domain}`;
    }

    riskScore.textContent = `${score}%`;
    riskLabel.textContent = label;

    if (score > 70) {
        resultBox.className = "result-box result-danger show";
        riskMessage.innerHTML = "⛔ <strong>High Risk Detected!</strong><br>This website shows strong phishing indicators. Do NOT enter personal information.";
    } else if (score > 40) {
        resultBox.className = "result-box result-suspicious show";
        riskMessage.innerHTML = "⚠️ <strong>Suspicious Activity</strong><br>Multiple risk indicators detected. Verify this website before proceeding.";
    } else if (score > 20) {
        resultBox.className = "result-box result-caution show";
        riskMessage.innerHTML = "🔶 <strong>Unknown Domain</strong><br>This is not a recognized trusted domain. Proceed with reasonable caution.";
    } else {
        resultBox.className = "result-box result-safe show";
        riskMessage.innerHTML = "✅ <strong>Website Appears Safe</strong><br>This domain is recognized and trusted. No threats detected.";
    }

    if (trust === "trusted") {
        trustBadge.innerHTML = '<span class="trust-badge trust-trusted">🛡️ Trusted</span>';
    } else if (trust === "browser") {
        trustBadge.innerHTML = '<span class="trust-badge trust-browser">ℹ️ Browser Page</span>';
    } else {
        trustBadge.innerHTML = '<span class="trust-badge trust-unknown">❓ Unknown</span>';
    }

    if (flags.length > 0) {
        flagsList.innerHTML = flags.map(f => `<span class="flag-chip">${escapeHtml(f)}</span>`).join("");
        flagsContainer.className = "flags-section show";
    } else {
        flagsContainer.className = "flags-section";
    }

    const modelType = data.model_type || "";
    const modelAcc = data.model_accuracy || 0;
    if (modelAcc > 0) {
        modelBadge.innerHTML = `🧠 <strong>AI Model</strong> — ${modelAcc}% accuracy`;
    }
}

// =============================
// SHOW ERROR
// =============================

function showError(message) {
    resultBox.className = "result-box result-error show";
    domainDisplay.textContent = "";
    riskLabel.textContent = "Error";
    riskScore.textContent = "⚠️";
    riskMessage.textContent = message;
    trustBadge.innerHTML = "";
    flagsContainer.className = "flags-section";
}

// =============================
// EVENT LISTENERS
// =============================

// Manual scan
scanBtn.addEventListener("click", scanWebsite);

// Auto-scan toggle
autoScanToggle.addEventListener("change", (e) => {
    chrome.storage.sync.set({ [AUTO_SCAN_KEY]: e.target.checked });
    if (e.target.checked && currentUrl && !isScanning) {
        scanWebsite();
    }
});

// Auto-block toggle
autoBlockToggle.addEventListener("change", (e) => {
    chrome.storage.sync.set({ [AUTO_BLOCK_KEY]: e.target.checked });
});

// Protection level select
protectionLevel.addEventListener("change", (e) => {
    chrome.storage.sync.set({ [PROTECTION_LEVEL_KEY]: e.target.value });
});

// Recent blocks expandable
let recentBlocksOpen = false;
recentBlocksHeader.addEventListener("click", () => {
    recentBlocksOpen = !recentBlocksOpen;
    if (recentBlocksOpen) {
        recentBlocksHeader.classList.add("open");
        recentBlocksList.classList.add("show");
    } else {
        recentBlocksHeader.classList.remove("open");
        recentBlocksList.classList.remove("show");
    }
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.active) {
        chrome.storage.sync.get([AUTO_SCAN_KEY], (result) => {
            if (result[AUTO_SCAN_KEY] !== false) {
                currentUrl = tab.url;
                urlDisplay.textContent = currentUrl;
                scanWebsite();
            }
        });
    }
});

// =============================
// START
// =============================

initialize();
