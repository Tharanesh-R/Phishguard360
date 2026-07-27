# CyberShield Browser Extension

## 🛡️ AI-Powered Phishing Detection Extension

CyberShield is a Chrome browser extension that uses artificial intelligence to detect phishing websites in real-time. It provides automatic scanning of websites as you browse and gives instant risk assessments.

---

## ✨ Features

- **🔄 Automatic Scanning**: Automatically scans websites when you navigate to them
- **🎯 Manual Scan Option**: Click to scan any website on-demand
- **📊 Risk Score Display**: Shows detailed risk percentage and threat level
- **🎨 Modern UI**: Beautiful, intuitive interface with visual feedback
- **💾 Persistent Settings**: Remembers your auto-scan preference
- **🔌 Backend Status**: Real-time connection status to the AI backend
- **⚡ Fast Analysis**: Quick phishing detection using ML model

---

## 📋 Prerequisites

Before installing the extension, ensure you have:

1. **Google Chrome** browser (or Chromium-based browser like Edge, Brave)
2. **Python 3.7+** installed
3. **Flask backend** running (see Backend Setup below)

---

## 🚀 Installation Guide

### Step 1: Backend Setup

1. **Navigate to the project directory**:
   ```bash
   cd e:\CyberShield_Advanced_Full
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server**:
   ```bash
   python app.py
   ```

   You should see:
   ```
   * Running on http://127.0.0.1:5000
   ```

   ⚠️ **Keep this terminal window open** - the backend must be running for the extension to work.

### Step 2: Load Extension in Chrome

1. **Open Chrome** and navigate to:
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode**:
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the Extension**:
   - Click "Load unpacked"
   - Navigate to: `e:\CyberShield_Advanced_Full\extension`
   - Click "Select Folder"

4. **Verify Installation**:
   - You should see "CyberShield" in your extensions list
   - The extension icon should appear in your Chrome toolbar

---

## 📖 How to Use

### Automatic Scanning (Default)

1. **Navigate to any website**
2. **Click the CyberShield icon** in your toolbar
3. The extension will **automatically scan** the current page
4. View the **risk score** and **threat assessment**

### Manual Scanning

1. Click the CyberShield icon
2. Click the **"🔍 Scan This Website"** button
3. Wait for analysis results

### Toggle Auto-Scan

- Use the **"🔄 Auto-Scan on Page Load"** toggle to enable/disable automatic scanning
- Your preference is saved automatically

---

## 🎨 Understanding Results

### Risk Levels

| Risk Score | Label | Meaning |
|------------|-------|---------|
| **0-40%** | ✅ Safe | Website appears legitimate |
| **41-70%** | ⚠️ Suspicious | Exercise caution, verify authenticity |
| **71-100%** | ⚠️ Phishing | High risk - avoid entering sensitive data |

### Visual Indicators

- **Green**: Safe website
- **Yellow**: Suspicious activity detected
- **Red**: High phishing risk
- **Blue**: Scanning in progress

---

## 🔧 Troubleshooting

### "Backend Offline" Error

**Problem**: Extension shows "Backend Offline" in the footer

**Solution**:
1. Ensure Flask server is running: `python app.py`
2. Check that it's running on `http://127.0.0.1:5000`
3. Verify no firewall is blocking port 5000

### "Unable to Connect to Backend" Error

**Problem**: Scan fails with connection error

**Solution**:
1. Restart the Flask server
2. Check the terminal for any Python errors
3. Ensure `modern_phishing_model.pkl` exists in the project directory
4. Try reloading the extension in Chrome

### Extension Not Appearing

**Problem**: Extension icon not visible in toolbar

**Solution**:
1. Go to `chrome://extensions/`
2. Verify CyberShield is enabled
3. Click the puzzle icon in Chrome toolbar
4. Pin CyberShield to toolbar

### Auto-Scan Not Working

**Problem**: Websites aren't scanned automatically

**Solution**:
1. Click the extension icon
2. Ensure "Auto-Scan on Page Load" toggle is **ON** (purple)
3. Navigate to a new website to test
4. Check that backend is online

---

## 🔒 Privacy & Security

- **No Data Collection**: The extension does not collect or store personal data
- **Local Processing**: All analysis is done locally on your machine
- **No External Servers**: Data is only sent to your local Flask backend
- **Open Source**: Full transparency - review the code yourself

---

## 🛠️ Technical Details

### Architecture

```
Browser Extension (popup.js)
        ↓
    HTTP Request
        ↓
Flask Backend (app.py)
        ↓
ML Model (modern_phishing_model.pkl)
        ↓
    Risk Assessment
        ↓
    JSON Response
        ↓
Extension UI (popup.html)
```

### API Endpoint

**POST** `/api/predict`

Request:
```json
{
  "url": "https://example.com"
}
```

Response:
```json
{
  "risk_score": 15.5,
  "label": "✅ Safe"
}
```

---

## 📝 Development

### File Structure

```
extension/
├── manifest.json       # Extension configuration
├── popup.html         # UI interface
├── popup.js           # Main logic
└── README.md          # This file
```

### Permissions Used

- `activeTab`: Access current tab URL
- `scripting`: Execute scripts if needed
- `storage`: Save user preferences
- `tabs`: Monitor page navigation for auto-scan

---

## 🐛 Known Issues

- Extension requires backend to be running locally
- Only works with HTTP/HTTPS URLs
- Chrome extension pages (chrome://) cannot be scanned

---

## 🔄 Updates

### Version 3.1 (Current)
- ✅ Added automatic scanning on page load
- ✅ Implemented modern, responsive UI
- ✅ Added backend status indicator
- ✅ Persistent auto-scan preferences
- ✅ Enhanced error handling
- ✅ Visual feedback improvements

### Version 3.0
- Initial release with manual scanning

---

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Verify backend is running: `http://127.0.0.1:5000/test`
3. Check browser console for errors (F12 → Console)
4. Review Flask terminal for backend errors

---

## 📄 License

This project is part of the CyberShield Advanced security suite.

---

## 🎯 Quick Start Checklist

- [ ] Python installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Flask backend running (`python app.py`)
- [ ] Extension loaded in Chrome
- [ ] Extension icon visible in toolbar
- [ ] Backend status shows "Online"
- [ ] Test scan successful

---

**Stay Safe Online! 🛡️**
