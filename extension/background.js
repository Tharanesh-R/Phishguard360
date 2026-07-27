// ================================================
// CyberShield — Fortinet-Style Auto-Blocking Engine
// ================================================

const BACKEND_URL = "http://127.0.0.1:5000";

// Storage keys
const AUTO_BLOCK_KEY = "cybershield_auto_block";
const PROTECTION_LEVEL_KEY = "cybershield_protection_level";
const BLOCKED_LOG_KEY = "cybershield_blocked_log";
const BLOCK_COUNT_KEY = "cybershield_block_count_today";
const BLOCK_COUNT_DATE_KEY = "cybershield_block_count_date";

// Protection level thresholds (Fortinet-style)
const PROTECTION_LEVELS = {
    strict: { threshold: 30, label: "Strict" },
    standard: { threshold: 50, label: "Standard" },
    permissive: { threshold: 70, label: "Permissive" }
};

// Local URL cache (domain -> { block, data, expiry })
const urlCache = new Map();
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

// Tracking sets to prevent duplicate scans
const blockedTabCache = new Map();
const scanInFlight = new Set();

// =============================
// UTILITIES
// =============================

function isScannableUrl(url) {
    if (!url || typeof url !== "string") return false;
    return url.startsWith("http://") || url.startsWith("https://");
}

function isBlockPageUrl(url) {
    return typeof url === "string" && url.startsWith(chrome.runtime.getURL("block.html"));
}

function extractDomain(url) {
    try {
        const u = new URL(url);
        let host = u.hostname.toLowerCase();
        if (host.startsWith("www.")) host = host.slice(4);
        return host;
    } catch { return ""; }
}

function getTodayDateStr() {
    return new Date().toISOString().slice(0, 10);
}

// =============================
// CACHE MANAGEMENT
// =============================

function getCachedResult(url) {
    const domain = extractDomain(url);
    const cached = urlCache.get(domain);
    if (cached && Date.now() < cached.expiry) {
        return cached;
    }
    urlCache.delete(domain);
    return null;
}

function setCachedResult(url, data) {
    const domain = extractDomain(url);
    urlCache.set(domain, {
        block: data.block,
        data: data,
        expiry: Date.now() + CACHE_TTL_MS
    });

    // Keep cache reasonable size
    if (urlCache.size > 500) {
        const oldest = urlCache.keys().next().value;
        urlCache.delete(oldest);
    }
}

// =============================
// SETTINGS
// =============================

async function getAutoBlockEnabled() {
    return new Promise((resolve) => {
        chrome.storage.sync.get([AUTO_BLOCK_KEY], (result) => {
            if (chrome.runtime.lastError) { resolve(true); return; }
            resolve(result[AUTO_BLOCK_KEY] !== false);
        });
    });
}

async function getProtectionLevel() {
    return new Promise((resolve) => {
        chrome.storage.sync.get([PROTECTION_LEVEL_KEY], (result) => {
            if (chrome.runtime.lastError) { resolve("standard"); return; }
            const level = result[PROTECTION_LEVEL_KEY] || "standard";
            resolve(PROTECTION_LEVELS[level] ? level : "standard");
        });
    });
}

async function getThreshold() {
    const level = await getProtectionLevel();
    return PROTECTION_LEVELS[level].threshold;
}

// =============================
// BADGE MANAGEMENT
// =============================

async function incrementBlockCount() {
    return new Promise((resolve) => {
        const today = getTodayDateStr();
        chrome.storage.local.get([BLOCK_COUNT_KEY, BLOCK_COUNT_DATE_KEY], (result) => {
            let count = 0;
            if (result[BLOCK_COUNT_DATE_KEY] === today) {
                count = (result[BLOCK_COUNT_KEY] || 0);
            }
            count++;
            chrome.storage.local.set({
                [BLOCK_COUNT_KEY]: count,
                [BLOCK_COUNT_DATE_KEY]: today
            }, () => {
                updateBadge(count);
                resolve(count);
            });
        });
    });
}

function updateBadge(count) {
    if (count > 0) {
        chrome.action.setBadgeText({ text: String(count) });
        chrome.action.setBadgeBackgroundColor({ color: "#ef4444" });
    } else {
        chrome.action.setBadgeText({ text: "" });
    }
}

async function refreshBadge() {
    const today = getTodayDateStr();
    chrome.storage.local.get([BLOCK_COUNT_KEY, BLOCK_COUNT_DATE_KEY], (result) => {
        if (result[BLOCK_COUNT_DATE_KEY] === today) {
            updateBadge(result[BLOCK_COUNT_KEY] || 0);
        } else {
            updateBadge(0);
        }
    });
}

// =============================
// BLOCKED LOG
// =============================

async function addToBlockedLog(entry) {
    return new Promise((resolve) => {
        chrome.storage.local.get([BLOCKED_LOG_KEY], (result) => {
            let log = result[BLOCKED_LOG_KEY] || [];
            log.unshift({
                url: entry.url,
                domain: entry.domain,
                category: entry.category || "Unknown",
                risk_score: entry.risk_score,
                label: entry.label,
                flags: (entry.flags || []).slice(0, 5),
                timestamp: new Date().toISOString(),
                blocklist_hit: entry.blocklist_hit || false
            });
            // Keep last 50 entries
            if (log.length > 50) log = log.slice(0, 50);
            chrome.storage.local.set({ [BLOCKED_LOG_KEY]: log }, resolve);
        });
    });
}

// =============================
// BLOCK PAGE
// =============================

function buildBlockPageUrl(data, originalUrl) {
    const params = new URLSearchParams({
        original: originalUrl,
        risk: String(data.risk_score ?? 0),
        label: data.label || "Blocked",
        domain: data.domain || "Unknown",
        category: data.category || "Threat Detected",
        reason: (data.flags || []).slice(0, 5).join(" | "),
        blocklist: data.blocklist_hit ? "true" : "false",
        time: new Date().toISOString()
    });
    return `${chrome.runtime.getURL("block.html")}?${params.toString()}`;
}

// =============================
// BACKEND API CALL
// =============================

async function checkUrlWithBackend(url, threshold) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
        const response = await fetch(`${BACKEND_URL}/api/check_block`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, threshold }),
            signal: controller.signal
        });

        clearTimeout(timeout);

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        clearTimeout(timeout);
        throw error;
    }
}

// =============================
// CORE: NAVIGATION HANDLER
// =============================

async function handleNavigation(tabId, url, source = "unknown") {
    if (!isScannableUrl(url)) return;
    if (isBlockPageUrl(url)) return;

    const autoBlockEnabled = await getAutoBlockEnabled();
    if (!autoBlockEnabled) return;

    // Prevent blocking the same URL twice on a tab
    const alreadyBlocked = blockedTabCache.get(tabId);
    if (alreadyBlocked === url) return;

    // Prevent duplicate in-flight scans
    const inflightKey = `${tabId}:${url}`;
    if (scanInFlight.has(inflightKey)) return;
    scanInFlight.add(inflightKey);

    try {
        const threshold = await getThreshold();

        // Check local cache first — if cached, content script will handle it
        const cached = getCachedResult(url);
        if (cached) {
            if (cached.block) {
                blockedTabCache.set(tabId, url);
            }
            return;
        }

        // Pre-fetch and cache for the content script
        console.debug("[CyberShield] Pre-caching:", { tabId, source, url });
        const data = await checkUrlWithBackend(url, threshold);

        if (data.error) {
            console.error("[CyberShield] API error:", data.error);
            return;
        }

        // Cache the result — content script will use this
        setCachedResult(url, data);

        if (data.block) {
            blockedTabCache.set(tabId, url);
            console.warn("[CyberShield] ⛔ Threat detected (content script will block):", {
                url,
                risk: data.risk_score,
                category: data.category
            });
        }
    } catch (error) {
        console.error("[CyberShield] Pre-cache scan failed:", error.message);
    } finally {
        scanInFlight.delete(inflightKey);
    }
}

// =============================
// EVENT LISTENERS
// =============================

// Pre-navigation interception (Fortinet-style: block BEFORE page loads)
if (chrome.webNavigation && chrome.webNavigation.onBeforeNavigate) {
    chrome.webNavigation.onBeforeNavigate.addListener((details) => {
        if (details.frameId !== 0) return; // Only main frame
        handleNavigation(details.tabId, details.url, "onBeforeNavigate");
    });
}

// Tab URL changes
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    const candidateUrl = changeInfo.url || (changeInfo.status === "complete" ? tab?.url : "");
    if (!candidateUrl) return;
    handleNavigation(tabId, candidateUrl, "tabs.onUpdated");
});

// Tab activated (user switches tabs)
chrome.tabs.onActivated.addListener(async ({ tabId }) => {
    try {
        const tab = await chrome.tabs.get(tabId);
        if (tab?.url) {
            handleNavigation(tabId, tab.url, "tabs.onActivated");
        }
    } catch (error) {
        console.error("[CyberShield] Failed to scan active tab:", error);
    }
});

// SPA navigation
if (chrome.webNavigation && chrome.webNavigation.onHistoryStateUpdated) {
    chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
        if (details.frameId !== 0) return;
        handleNavigation(details.tabId, details.url, "onHistoryStateUpdated");
    });
}

// Cleanup on tab close
chrome.tabs.onRemoved.addListener((tabId) => {
    blockedTabCache.delete(tabId);
});

// =============================
// NATIVE MESSAGING HOST NAME
// =============================

const NATIVE_HOST_NAME = "com.cybershield.backend";
let backendStartAttempts = 0;
const MAX_START_ATTEMPTS = 3;

// =============================
// AUTO-START BACKEND
// =============================

async function isBackendRunning() {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 2000);
        const response = await fetch(`${BACKEND_URL}/test`, {
            signal: controller.signal
        });
        clearTimeout(timeout);
        return response.ok;
    } catch {
        return false;
    }
}

async function startBackendViaNativeMessaging() {
    return new Promise((resolve) => {
        try {
            const port = chrome.runtime.connectNative(NATIVE_HOST_NAME);

            let responded = false;

            port.onMessage.addListener((msg) => {
                responded = true;
                console.log("[CyberShield] Native host response:", msg);

                if (msg.status === "started" || msg.status === "already_running") {
                    console.log("[CyberShield] ✅ Backend is running on port", msg.port);
                    resolve(true);
                } else if (msg.status === "timeout") {
                    console.warn("[CyberShield] Backend started but port not ready yet");
                    resolve(true); // It may still come up
                } else {
                    console.error("[CyberShield] Backend start failed:", msg.message);
                    resolve(false);
                }
                port.disconnect();
            });

            port.onDisconnect.addListener(() => {
                if (!responded) {
                    const lastError = chrome.runtime.lastError;
                    console.error("[CyberShield] Native messaging error:",
                        lastError ? lastError.message : "Disconnected");

                    if (lastError && lastError.message.includes("not found")) {
                        console.error("[CyberShield] ⚠️ Native host not installed!");
                        console.error("[CyberShield] Run: python install.py");
                    }
                    resolve(false);
                }
            });

            // Send start command
            port.postMessage({ action: "start_server" });

        } catch (error) {
            console.error("[CyberShield] Native messaging not available:", error);
            resolve(false);
        }
    });
}

async function ensureBackendRunning() {
    // Check if already running
    const running = await isBackendRunning();
    if (running) {
        console.log("[CyberShield] ✅ Backend already running");
        return true;
    }

    // Try to start via native messaging
    if (backendStartAttempts >= MAX_START_ATTEMPTS) {
        console.error("[CyberShield] Max start attempts reached. Please start manually: python app.py");
        return false;
    }

    backendStartAttempts++;
    console.log(`[CyberShield] Backend not running. Starting attempt ${backendStartAttempts}/${MAX_START_ATTEMPTS}...`);

    const started = await startBackendViaNativeMessaging();

    if (started) {
        // Wait and verify
        await new Promise(r => setTimeout(r, 2000));
        const verified = await isBackendRunning();
        if (verified) {
            console.log("[CyberShield] ✅ Backend verified running!");
            return true;
        }
    }

    // Retry after delay
    console.warn("[CyberShield] Retrying in 3 seconds...");
    await new Promise(r => setTimeout(r, 3000));
    return ensureBackendRunning();
}

// =============================
// INSTALL & STARTUP
// =============================

chrome.runtime.onInstalled.addListener(() => {
    // Set defaults
    chrome.storage.sync.get([AUTO_BLOCK_KEY, PROTECTION_LEVEL_KEY], (result) => {
        const defaults = {};
        if (result[AUTO_BLOCK_KEY] === undefined) defaults[AUTO_BLOCK_KEY] = true;
        if (result[PROTECTION_LEVEL_KEY] === undefined) defaults[PROTECTION_LEVEL_KEY] = "standard";
        if (Object.keys(defaults).length > 0) {
            chrome.storage.sync.set(defaults);
        }
    });
    refreshBadge();

    // Auto-start backend
    ensureBackendRunning();
    console.log("[CyberShield] Extension installed — auto-start enabled");
});

chrome.runtime.onStartup.addListener(() => {
    refreshBadge();

    // Auto-start backend when Chrome launches
    ensureBackendRunning();
    console.log("[CyberShield] Chrome started — auto-starting backend");
});

// =============================
// MESSAGE HANDLER (Content Script)
// =============================

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "SCAN_AND_BLOCK") {
        // Content script asks background to check a URL
        // Background makes the API call (has host_permissions, no CORS issues)
        (async () => {
            try {
                const autoBlockEnabled = await getAutoBlockEnabled();
                if (!autoBlockEnabled) {
                    sendResponse({ skip: true, block: false });
                    return;
                }

                const url = message.url;

                // Check local cache first
                const cached = getCachedResult(url);
                if (cached) {
                    sendResponse({ block: cached.block, data: cached.data, skip: false });
                    if (cached.block) {
                        await incrementBlockCount();
                        await addToBlockedLog({ ...cached.data, url });
                    }
                    return;
                }

                // Get threshold from protection level
                const threshold = await getThreshold();

                // Make API call from background (no CORS/mixed-content issues)
                const data = await checkUrlWithBackend(url, threshold);

                if (data.error) {
                    sendResponse({ block: false, skip: false });
                    return;
                }

                // Cache result
                setCachedResult(url, data);

                if (data.block) {
                    await incrementBlockCount();
                    await addToBlockedLog({ ...data, url });
                    console.warn("[CyberShield] ⛔ BLOCKED:", url, "Risk:", data.risk_score);
                }

                sendResponse({ block: data.block, data: data, skip: false });

            } catch (error) {
                console.error("[CyberShield] Scan error:", error.message);
                // Try auto-starting backend if it's down
                ensureBackendRunning();
                sendResponse({ block: false, skip: false });
            }
        })();
        return true; // keep channel open for async response
    }

    if (message.type === "URL_BLOCKED") {
        // Legacy: content script reports a block
        (async () => {
            await incrementBlockCount();
            await addToBlockedLog({ ...message.data, url: message.url });
            setCachedResult(message.url, message.data);
        })();
        return false;
    }
});

