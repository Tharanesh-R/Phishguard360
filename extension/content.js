// =====================================================
// CyberShield Content Script — Fortinet-Style Blocker
// Runs at document_start BEFORE any page content renders
// ALL API calls go through background.js (no direct fetch)
// =====================================================

(function () {
    "use strict";

    const currentUrl = window.location.href;

    // Skip non-http pages and extension pages
    if (!currentUrl.startsWith("http://") && !currentUrl.startsWith("https://")) return;
    if (currentUrl.includes("chrome-extension://")) return;

    // Create overlay IMMEDIATELY before anything else
    const overlay = createOverlay();

    // Send URL to background script for checking
    chrome.runtime.sendMessage(
        { type: "SCAN_AND_BLOCK", url: currentUrl },
        (response) => {
            if (chrome.runtime.lastError) {
                // Background unavailable — allow page
                removeOverlay(overlay);
                return;
            }

            if (!response) {
                removeOverlay(overlay);
                return;
            }

            if (response.skip) {
                // Auto-block is disabled
                removeOverlay(overlay);
                return;
            }

            if (response.block) {
                // BLOCK THE PAGE
                blockPage(response.data);
            } else {
                // Safe — allow page
                removeOverlay(overlay);
            }
        }
    );

    function createOverlay() {
        const overlay = document.createElement("div");
        overlay.id = "cybershield-scan-overlay";
        overlay.setAttribute("style", [
            "position:fixed !important",
            "top:0 !important",
            "left:0 !important",
            "width:100vw !important",
            "height:100vh !important",
            "background:#0a0e1a !important",
            "z-index:2147483647 !important",
            "display:flex !important",
            "align-items:center !important",
            "justify-content:center !important",
            "flex-direction:column !important",
            "font-family:Segoe UI,system-ui,-apple-system,sans-serif !important",
            "transition:opacity 0.3s ease !important"
        ].join(";"));

        overlay.innerHTML = `
            <style>
                @keyframes cs-spin { to { transform: rotate(360deg); } }
            </style>
            <div style="width:40px;height:40px;border:3px solid rgba(99,102,241,0.2);border-top-color:#6366f1;border-radius:50%;animation:cs-spin 0.7s linear infinite;margin-bottom:16px;"></div>
            <div style="color:#94a3b8;font-size:14px;font-weight:500;">
                <span style="color:#818cf8;font-weight:700;">🛡️ CyberShield</span> is scanning this page...
            </div>
        `;

        // Insert ASAP
        const tryInsert = () => {
            const target = document.documentElement || document.body;
            if (target) {
                target.appendChild(overlay);
            } else {
                requestAnimationFrame(tryInsert);
            }
        };
        tryInsert();

        return overlay;
    }

    function removeOverlay(el) {
        if (!el) return;
        el.style.opacity = "0";
        setTimeout(() => {
            try { el.parentNode && el.parentNode.removeChild(el); } catch (e) { }
        }, 300);
    }

    function blockPage(data) {
        const riskScore = data.risk_score || 0;
        const category = data.category || "Threat Detected";
        const label = data.label || "Blocked";
        const domain = data.domain || window.location.hostname;
        const flags = (data.flags || []).slice(0, 5);
        const isBlocklist = data.blocklist_hit || false;
        const now = new Date();

        const catIcons = {
            "phishing": "🎣", "malware": "🦠", "scam": "💰",
            "cryptomining": "⛏️", "command & control": "🖥️",
            "suspicious": "⚠️", "caution": "🔶"
        };
        const catLower = category.toLowerCase();
        const icon = catIcons[catLower] || "⛔";
        const riskColor = riskScore > 70 ? "#ef4444" : riskScore > 40 ? "#f59e0b" : "#10b981";
        const riskBarClass = riskScore > 70 ? "high" : riskScore > 40 ? "medium" : "low";
        const flagsHtml = flags.map(f =>
            `<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;margin:2px 3px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);border-radius:100px;font-size:11px;color:#fca5a5;">${isBlocklist ? '🛡️' : '⚡'} ${esc(f)}</span>`
        ).join("");

        // Stop any loading
        window.stop();

        // Replace entire page
        document.documentElement.innerHTML = `
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>CyberShield — Web Page Blocked!</title>
            <style>
                *{margin:0;padding:0;box-sizing:border-box}
                body{min-height:100vh;font-family:Segoe UI,system-ui,sans-serif;color:#f1f5f9;background:#0a0e1a;display:grid;place-items:center;padding:24px}
                body::before{content:'';position:fixed;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(ellipse at 20% 20%,rgba(239,68,68,0.08) 0%,transparent 50%),radial-gradient(ellipse at 80% 80%,rgba(99,102,241,0.06) 0%,transparent 50%);animation:bgP 8s ease-in-out infinite alternate;pointer-events:none;z-index:0}
                @keyframes bgP{0%{transform:scale(1);opacity:1}100%{transform:scale(1.1);opacity:.7}}
                .c{width:min(700px,100%);position:relative;z-index:1}
                .hb{background:linear-gradient(135deg,#1a1f36,#0f1425);border:1px solid rgba(255,255,255,.08);border-radius:16px 16px 0 0;padding:16px 22px;display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid rgba(239,68,68,.3)}
                .hl{display:flex;align-items:center;gap:10px}
                .hs{width:34px;height:34px;background:linear-gradient(135deg,#ef4444,#dc2626);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:17px;box-shadow:0 4px 15px rgba(239,68,68,.3);animation:sp 2s ease-in-out infinite}
                @keyframes sp{0%,100%{box-shadow:0 0 15px rgba(239,68,68,.3)}50%{box-shadow:0 0 30px rgba(239,68,68,.5)}}
                .ht{font-size:15px;font-weight:700;color:#f87171}
                .hst{font-size:10px;color:#64748b;font-weight:500}
                .hbdg{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#64748b;padding:4px 10px;border:1px solid rgba(255,255,255,.08);border-radius:100px}
                .cd{background:rgba(15,20,35,.95);border:1px solid rgba(255,255,255,.08);border-top:none;border-radius:0 0 16px 16px;padding:26px;box-shadow:0 25px 60px rgba(0,0,0,.4)}
                .cb{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:100px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(239,68,68,.25);margin-bottom:16px}
                .bt{font-size:clamp(1.2rem,2.5vw,1.6rem);font-weight:800;letter-spacing:-.5px;margin-bottom:8px}
                .bd{color:#94a3b8;font-size:13px;line-height:1.6;margin-bottom:22px}
                .rs{display:flex;align-items:center;gap:14px;padding:14px;margin-bottom:18px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px}
                .rn{font-size:36px;font-weight:800;letter-spacing:-2px;color:${riskColor};min-width:70px;text-align:center}
                .rbw{flex:1}
                .rbl{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#64748b;margin-bottom:5px}
                .rb{height:8px;background:rgba(255,255,255,.06);border-radius:8px;overflow:hidden}
                .rbf{height:100%;border-radius:8px;transition:width 1s cubic-bezier(.4,0,.2,1)}
                .rbf.high{background:linear-gradient(90deg,#ef4444,#f87171)}
                .rbf.medium{background:linear-gradient(90deg,#f59e0b,#fbbf24)}
                .rbf.low{background:linear-gradient(90deg,#10b981,#34d399)}
                .rlt{font-size:11px;color:#94a3b8;margin-top:5px}
                .ig{display:grid;gap:8px;margin-bottom:18px}
                .ir{display:flex;align-items:flex-start;gap:10px;padding:11px 13px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:10px}
                .ii{font-size:14px;flex-shrink:0}
                .il{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#64748b;margin-bottom:2px}
                .iv{font-size:12px;color:#f1f5f9;word-break:break-all;line-height:1.5}
                .fw{margin-bottom:20px}
                .fl{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#64748b;margin-bottom:8px}
                .ac{display:flex;gap:10px;flex-wrap:wrap}
                .bn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:11px 20px;border:none;border-radius:10px;font-size:13px;font-weight:600;font-family:inherit;cursor:pointer;transition:all .3s;text-decoration:none}
                .bp{background:linear-gradient(135deg,#6366f1,#818cf8);color:#fff;flex:1;box-shadow:0 4px 15px rgba(99,102,241,.3)}
                .bp:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(99,102,241,.45)}
                .bs{background:rgba(255,255,255,.06);color:#94a3b8;border:1px solid rgba(255,255,255,.08)}
                .bs:hover{background:rgba(255,255,255,.1);color:#f1f5f9}
                .ts{font-size:10px;color:#64748b;text-align:center;margin-top:10px}
                .ft{text-align:center;margin-top:16px;font-size:10px;color:#64748b}
                .fb{font-weight:700;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
            </style>
        </head>
        <body>
            <div class="c">
                <div class="hb">
                    <div class="hl">
                        <div class="hs">🛡️</div>
                        <div>
                            <div class="ht">CyberShield Web Filtering</div>
                            <div class="hst">AI-Powered Threat Prevention</div>
                        </div>
                    </div>
                    <div class="hbdg">Auto-Block</div>
                </div>
                <div class="cd">
                    <div class="cb">${icon} ${esc(category)}</div>
                    <div class="bt">Web Page Blocked!</div>
                    <div class="bd">The page you have requested has been blocked because it was identified as a <strong>security threat</strong>. CyberShield is protecting your device and personal data.</div>
                    <div class="rs">
                        <div class="rn">${Math.round(riskScore)}%</div>
                        <div class="rbw">
                            <div class="rbl">Threat Level</div>
                            <div class="rb"><div class="rbf ${riskBarClass}" id="rbf" style="width:0%"></div></div>
                            <div class="rlt">${esc(label)}</div>
                        </div>
                    </div>
                    <div class="ig">
                        <div class="ir"><span class="ii">🌐</span><div><div class="il">Blocked Domain</div><div class="iv">${esc(domain)}</div></div></div>
                        <div class="ir"><span class="ii">🔗</span><div><div class="il">URL</div><div class="iv">${esc(currentUrl)}</div></div></div>
                    </div>
                    ${flagsHtml ? `<div class="fw"><div class="fl">Detection Details</div><div>${flagsHtml}</div></div>` : ""}
                    <div class="ac">
                        <button class="bn bp" id="goBackBtn">← Go Back to Safety</button>
                        <button class="bn bs" id="closeBtn">✕ Close Tab</button>
                    </div>
                    <div class="ts">Blocked at ${now.toLocaleTimeString()} on ${now.toLocaleDateString()}</div>
                </div>
                <div class="ft">Protected by <span class="fb">CyberShield</span> — AI-Powered Threat Prevention</div>
            </div>
        </body>`;

        // IMPORTANT: Inline <script> tags don't execute in content script context (CSP).
        // Attach event listeners and animate risk bar programmatically instead.
        setTimeout(() => {
            // Animate risk bar fill
            const barEl = document.getElementById('rbf');
            if (barEl) barEl.style.width = Math.min(riskScore, 100) + '%';

            // Go Back to Safety button
            const goBackBtn = document.getElementById('goBackBtn');
            if (goBackBtn) {
                goBackBtn.addEventListener('click', () => {
                    if (window.history.length > 1) {
                        window.history.go(-1);
                    } else {
                        window.location.href = 'https://www.google.com';
                    }
                });
            }

            // Close Tab button
            const closeBtn = document.getElementById('closeBtn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    window.close();
                    // Fallback if window.close() is blocked
                    window.location.href = 'about:blank';
                });
            }
        }, 50);
    }

    function esc(s) {
        const d = document.createElement("div");
        d.textContent = s || "";
        return d.innerHTML;
    }
})();

