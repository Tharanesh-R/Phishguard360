# 📸 Visual Installation Guide

## Step 1: Start the Backend

### Option A: Using the Setup Script (Recommended)
```
1. Navigate to: e:\CyberShield_Advanced_Full
2. Double-click: setup_extension.bat
3. Follow the prompts
4. Press 'Y' when asked to start backend
```

### Option B: Manual Start
```
1. Open Command Prompt
2. cd e:\CyberShield_Advanced_Full
3. python app.py
```

**You should see:**
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

✅ **Backend is now running!** Keep this window open.

---

## Step 2: Open Chrome Extensions

### Method 1: Via URL Bar
```
1. Open Google Chrome
2. Type in address bar: chrome://extensions/
3. Press Enter
```

### Method 2: Via Menu
```
1. Click the three dots (⋮) in top-right
2. Click "Extensions"
3. Click "Manage Extensions"
```

---

## Step 3: Enable Developer Mode

```
┌─────────────────────────────────────────────┐
│ Extensions                                   │
│                                              │
│ Developer mode                          [OFF]│ ← Click this toggle
└─────────────────────────────────────────────┘
```

After clicking, it should show:
```
┌─────────────────────────────────────────────┐
│ Extensions                                   │
│                                              │
│ Developer mode                          [ON] │ ← Now ON
│                                              │
│ [Load unpacked] [Pack extension] [Update]   │ ← New buttons appear
└─────────────────────────────────────────────┘
```

---

## Step 4: Load the Extension

```
1. Click "Load unpacked" button
2. A file browser window opens
3. Navigate to: e:\CyberShield_Advanced_Full\extension
4. Click "Select Folder"
```

**File structure you should see:**
```
extension/
├── manifest.json          ← Must be present
├── popup.html
├── popup.js
├── README.md
├── QUICKSTART.md
└── IMPROVEMENTS.md
```

---

## Step 5: Verify Installation

You should now see:

```
┌─────────────────────────────────────────────┐
│ CyberShield                             v3.1│
│ AI-Powered Phishing Detector with Auto-Scan │
│                                              │
│ ID: abcdefghijklmnopqrstuvwxyz              │
│ Inspect views: popup.html                   │
│                                              │
│ [Details] [Remove] [Errors]                 │
└─────────────────────────────────────────────┘
```

✅ **Extension is loaded!**

---

## Step 6: Pin the Extension

```
1. Look for the puzzle piece icon (🧩) in Chrome toolbar
2. Click it to see all extensions
3. Find "CyberShield"
4. Click the pin icon (📌) next to it
```

**Result:**
```
Chrome Toolbar:
[← →] [🔄] [🏠] [...] [🛡️] [🧩] [👤]
                        ↑
                  CyberShield icon
```

---

## Step 7: Test the Extension

### First Test - Google.com

```
1. Navigate to: https://google.com
2. Click the CyberShield icon (🛡️)
3. Extension popup opens
4. Automatic scan starts immediately
```

**What you'll see:**

**During Scan:**
```
┌─────────────────────────────────┐
│  🛡️ CyberShield                 │
│  AI-Powered Phishing Detection  │
├─────────────────────────────────┤
│  https://google.com             │
├─────────────────────────────────┤
│  🔄 Auto-Scan on Page Load  [✓] │
├─────────────────────────────────┤
│  [⏳ Scanning...]               │
├─────────────────────────────────┤
│  Analyzing URL...               │
│         ⌛                      │
│  Please wait...                 │
├─────────────────────────────────┤
│  🟢 Backend Online              │
└─────────────────────────────────┘
```

**After Scan (Safe Result):**
```
┌─────────────────────────────────┐
│  🛡️ CyberShield                 │
│  AI-Powered Phishing Detection  │
├─────────────────────────────────┤
│  https://google.com             │
├─────────────────────────────────┤
│  🔄 Auto-Scan on Page Load  [✓] │
├─────────────────────────────────┤
│  [🔍 Scan This Website]         │
├─────────────────────────────────┤
│  ✅ Website Appears Safe        │
│         12.3%                   │
│  No immediate threats detected  │
│  Stay vigilant online.          │
├─────────────────────────────────┤
│  🟢 Backend Online              │
└─────────────────────────────────┘
```

---

## Understanding the Results

### 🟢 Safe (0-40% Risk)
```
┌─────────────────────────────────┐
│  ✅ Website Appears Safe        │
│         15.5%                   │
│  No immediate threats detected  │
│  Stay vigilant online.          │
└─────────────────────────────────┘
```
**Meaning**: Low risk, safe to browse

### 🟡 Suspicious (41-70% Risk)
```
┌─────────────────────────────────┐
│  ⚠️ Suspicious Activity         │
│         55.2%                   │
│  Exercise caution. Verify the   │
│  website's authenticity.        │
└─────────────────────────────────┘
```
**Meaning**: Medium risk, be careful

### 🔴 Phishing (71-100% Risk)
```
┌─────────────────────────────────┐
│  ⚠️ High Risk Detected!         │
│         87.3%                   │
│  This may be a phishing attempt │
│  Avoid entering sensitive info  │
└─────────────────────────────────┘
```
**Meaning**: High risk, avoid this site!

---

## Using the Auto-Scan Toggle

### To Disable Auto-Scan:
```
1. Click the CyberShield icon
2. Click the toggle switch to OFF
3. It will turn gray
```

**Before (Auto-Scan ON):**
```
🔄 Auto-Scan on Page Load  [✓]
                            ↑
                         Purple
```

**After (Auto-Scan OFF):**
```
🔄 Auto-Scan on Page Load  [ ]
                            ↑
                          Gray
```

### To Re-enable:
```
1. Click the toggle again
2. It turns purple
3. Current page is scanned immediately
```

---

## Manual Scanning

Even with auto-scan off, you can scan manually:

```
1. Click CyberShield icon
2. Click "🔍 Scan This Website" button
3. Wait for results
```

---

## Troubleshooting Visual Guide

### Problem: Backend Offline

**What you see:**
```
┌─────────────────────────────────┐
│  🔴 Backend Offline             │
│  Please start Flask server      │
└─────────────────────────────────┘
```

**Solution:**
```
1. Open Command Prompt
2. cd e:\CyberShield_Advanced_Full
3. python app.py
4. Wait for "Running on http://127.0.0.1:5000"
5. Click extension icon again
```

---

### Problem: Extension Not Visible

**What you see:**
```
Chrome Toolbar:
[← →] [🔄] [🏠] [...] [🧩] [👤]
                        ↑
                   No shield icon
```

**Solution:**
```
1. Click puzzle icon (🧩)
2. Find "CyberShield"
3. Click pin icon (📌)
4. Shield icon (🛡️) appears in toolbar
```

---

### Problem: "Unable to Connect"

**What you see:**
```
┌─────────────────────────────────┐
│  ⚠️ Error                       │
│  Unable to connect to backend   │
│  Please ensure Flask server is  │
│  running on port 5000           │
└─────────────────────────────────┘
```

**Solution:**
```
1. Check Flask is running (see terminal)
2. Test backend: http://127.0.0.1:5000/test
3. Should see: "CyberShield backend running"
4. If not, restart Flask server
```

---

## Daily Usage Workflow

### Morning Setup
```
1. Start computer
2. Open Command Prompt
3. cd e:\CyberShield_Advanced_Full
4. python app.py
5. Minimize terminal (keep it running)
```

### While Browsing
```
1. Browse normally
2. Extension auto-scans each page
3. Click icon to see results anytime
4. Check risk score before entering passwords
```

### End of Day
```
1. Go to Flask terminal
2. Press Ctrl+C to stop server
3. Close terminal
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════╗
║         CyberShield Quick Reference       ║
╠═══════════════════════════════════════════╣
║ Start Backend:                            ║
║   python app.py                           ║
║                                           ║
║ Load Extension:                           ║
║   chrome://extensions/                    ║
║   → Developer Mode ON                     ║
║   → Load unpacked                         ║
║   → Select extension folder               ║
║                                           ║
║ Risk Levels:                              ║
║   🟢 0-40%   = Safe                       ║
║   🟡 41-70%  = Suspicious                 ║
║   🔴 71-100% = Phishing                   ║
║                                           ║
║ Keyboard Shortcuts:                       ║
║   Alt+Shift+S = Open extension (custom)   ║
║                                           ║
║ Backend Test:                             ║
║   http://127.0.0.1:5000/test              ║
╚═══════════════════════════════════════════╝
```

---

## Success Indicators

✅ **Everything is working if you see:**

1. Terminal shows: `Running on http://127.0.0.1:5000`
2. Extension icon (🛡️) visible in Chrome toolbar
3. Backend status shows: `🟢 Backend Online`
4. Clicking icon shows current URL
5. Auto-scan completes within 1-2 seconds
6. Risk score displays with color coding

---

## Next Steps

1. ✅ Test on multiple websites
2. ✅ Try toggling auto-scan on/off
3. ✅ Test manual scan button
4. ✅ Check different risk levels
5. ✅ Verify backend status indicator
6. ✅ Read full documentation in README.md

---

**Congratulations! You're now protected by CyberShield! 🛡️**

For detailed information, see:
- **README.md** - Complete documentation
- **QUICKSTART.md** - Quick setup guide
- **IMPROVEMENTS.md** - Feature list
