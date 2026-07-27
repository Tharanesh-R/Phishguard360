# 🚀 Quick Start Guide - CyberShield Extension

## Step-by-Step Setup (5 Minutes)

### 1️⃣ Start the Backend Server

Open a terminal/command prompt and run:

```bash
cd e:\CyberShield_Advanced_Full
python app.py
```

✅ **Success**: You should see:
```
* Running on http://127.0.0.1:5000
```

⚠️ **Keep this window open!** The extension needs the backend running.

---

### 2️⃣ Load Extension in Chrome

1. Open Chrome and go to: **chrome://extensions/**

2. Enable **Developer mode** (toggle in top-right)

3. Click **"Load unpacked"**

4. Select folder: **e:\CyberShield_Advanced_Full\extension**

5. Click **"Select Folder"**

✅ **Success**: You'll see "CyberShield" in your extensions list

---

### 3️⃣ Test the Extension

1. **Navigate to any website** (e.g., google.com)

2. **Click the CyberShield icon** in your Chrome toolbar
   - If you don't see it, click the puzzle icon and pin CyberShield

3. **Watch it scan automatically!**
   - The extension will show:
     - Current URL
     - Scanning animation
     - Risk score (0-100%)
     - Safety assessment

---

## 🎯 What You'll See

### Safe Website (0-40% risk)
```
✅ Website Appears Safe
15.5%
No immediate threats detected. Stay vigilant online.
```

### Suspicious Website (41-70% risk)
```
⚠️ Suspicious Activity
55.2%
Exercise caution. Verify the website's authenticity before proceeding.
```

### Phishing Website (71-100% risk)
```
⚠️ High Risk Detected!
87.3%
This website may be a phishing attempt. Avoid entering sensitive information.
```

---

## 🔄 Features to Try

### ✅ Automatic Scanning
- Navigate to different websites
- Extension scans each page automatically
- Results appear instantly

### ✅ Manual Scanning
- Click "🔍 Scan This Website" button
- Useful for re-scanning after changes

### ✅ Toggle Auto-Scan
- Turn off auto-scan if you prefer manual control
- Toggle remembers your preference

### ✅ Backend Status
- Green dot = Backend online ✅
- Red dot = Backend offline ❌

---

## 🧪 Test URLs

Try scanning these to see different risk levels:

**Safe URLs:**
- https://google.com
- https://github.com
- https://microsoft.com

**The extension analyzes:**
- URL length
- HTTPS usage
- Special characters (@, -)
- Number of dots and slashes
- Other phishing indicators

---

## ⚠️ Troubleshooting

### Problem: "Backend Offline"
**Fix**: Start Flask server with `python app.py`

### Problem: Extension not visible
**Fix**: Click puzzle icon → Pin CyberShield

### Problem: "Unable to connect"
**Fix**: 
1. Check Flask is running
2. Visit http://127.0.0.1:5000/test in browser
3. Should see "CyberShield backend running"

---

## 📱 Using the Extension

### First Time Setup
1. ✅ Backend running
2. ✅ Extension loaded
3. ✅ Auto-scan enabled (default)
4. ✅ Navigate to any site
5. ✅ Click extension icon
6. ✅ See results!

### Daily Use
1. Keep backend running in background
2. Browse normally
3. Click extension icon to see scan results
4. Extension auto-scans new pages

---

## 🎨 UI Guide

```
┌─────────────────────────────────┐
│  🛡️ CyberShield                 │
│  AI-Powered Phishing Detection  │
├─────────────────────────────────┤
│  Current URL:                   │
│  https://example.com            │
├─────────────────────────────────┤
│  🔄 Auto-Scan on Page Load  [✓] │
├─────────────────────────────────┤
│  [🔍 Scan This Website]         │
├─────────────────────────────────┤
│  ✅ Website Appears Safe        │
│         15.5%                   │
│  No immediate threats detected  │
├─────────────────────────────────┤
│  🟢 Backend Online              │
└─────────────────────────────────┘
```

---

## 💡 Pro Tips

1. **Keep Backend Running**: Start it when you boot your computer
2. **Pin Extension**: Keep it visible in toolbar for quick access
3. **Check Before Login**: Always scan before entering passwords
4. **Trust the Score**: Higher scores = higher risk
5. **Stay Updated**: Extension learns from the ML model

---

## ✅ Verification Checklist

Before using, verify:

- [ ] Flask backend running (terminal shows "Running on http://127.0.0.1:5000")
- [ ] Extension loaded in Chrome (visible in chrome://extensions/)
- [ ] Extension icon in toolbar (or accessible via puzzle icon)
- [ ] Backend status shows "Online" (green dot)
- [ ] Test scan works on google.com
- [ ] Auto-scan toggle works

---

## 🎓 Next Steps

1. **Customize Settings**: Toggle auto-scan based on preference
2. **Monitor Results**: Check risk scores regularly
3. **Report Issues**: Note any false positives/negatives
4. **Share Feedback**: Help improve the model

---

**You're all set! Browse safely with CyberShield! 🛡️**

For detailed documentation, see **README.md**
