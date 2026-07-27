# 🔧 Common Errors & Solutions

## Error: "Object of type float32 is not JSON serializable"

### ❌ Problem
```
Error
⚠️
Object of type float32 is not JSON serializable
```

### ✅ Solution
This error has been **FIXED** in the latest version of `app.py`.

**What was wrong:**
- The ML model returns NumPy `float32` values
- JSON can't serialize NumPy types, only native Python types
- The `risk_score` wasn't being converted properly

**What was fixed:**
```python
# Before (broken):
risk_score = round(prob * 100, 2)

# After (fixed):
risk_score = float(round(float(prob) * 100, 2))
```

### 🔄 How to Apply the Fix

1. **Restart the Flask backend**:
   ```bash
   # In the terminal where Flask is running:
   Press Ctrl+C to stop
   
   # Then restart:
   python app.py
   ```

2. **Test the extension again**:
   - Click the CyberShield icon
   - The error should be gone!

---

## Other Common Errors

### Error: "Backend Offline"

**Problem:** Extension shows "Backend Offline" or red dot

**Solution:**
```bash
cd e:\CyberShield_Advanced_Full
python app.py
```

**Verify:** Terminal should show `Running on http://127.0.0.1:5000`

---

### Error: "Unable to connect to backend"

**Problem:** Extension can't reach Flask server

**Solutions:**

1. **Check Flask is running**
   ```bash
   # Should see this in terminal:
   * Running on http://127.0.0.1:5000
   ```

2. **Test backend directly**
   - Open browser
   - Go to: `http://127.0.0.1:5000/test`
   - Should see: "CyberShield backend running"

3. **Check firewall**
   - Windows Firewall might be blocking port 5000
   - Allow Python through firewall

4. **Restart Flask**
   ```bash
   Ctrl+C (stop)
   python app.py (restart)
   ```

---

### Error: "No module named 'flask_cors'"

**Problem:** Missing dependency

**Solution:**
```bash
pip install flask-cors
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

---

### Error: "No module named 'sklearn'"

**Problem:** Missing scikit-learn

**Solution:**
```bash
pip install scikit-learn
```

---

### Error: "modern_phishing_model.pkl not found"

**Problem:** ML model file missing

**Solution:**
1. Verify file exists: `e:\CyberShield_Advanced_Full\modern_phishing_model.pkl`
2. If missing, you need to train/obtain the model
3. Check if file was moved or deleted

---

### Error: Extension not visible in Chrome

**Problem:** Can't find extension icon

**Solution:**
1. Click puzzle icon (🧩) in Chrome toolbar
2. Find "CyberShield"
3. Click pin icon (📌) to pin it
4. Shield icon should appear in toolbar

---

### Error: "Developer mode required"

**Problem:** Can't load unpacked extension

**Solution:**
1. Go to `chrome://extensions/`
2. Toggle "Developer mode" ON (top-right)
3. "Load unpacked" button should appear

---

### Error: Manifest parsing failed

**Problem:** Invalid manifest.json

**Solution:**
1. Check `manifest.json` for syntax errors
2. Ensure all quotes are properly closed
3. Verify JSON is valid (use JSONLint.com)
4. Re-download the extension files

---

### Error: Auto-scan not working

**Problem:** Pages aren't scanned automatically

**Solutions:**

1. **Check toggle is ON**
   - Click extension icon
   - Ensure "Auto-Scan on Page Load" is purple/enabled

2. **Reload extension**
   - Go to `chrome://extensions/`
   - Click reload icon (🔄) on CyberShield

3. **Check permissions**
   - Extension needs `tabs` permission
   - Verify in manifest.json

---

### Error: CORS policy blocking request

**Problem:** Browser blocks request to localhost

**Solution:**
This should be fixed with `flask-cors` installed.

If still occurring:
```bash
pip install flask-cors
```

Then restart Flask:
```bash
python app.py
```

---

### Error: Port 5000 already in use

**Problem:** Another app is using port 5000

**Solutions:**

1. **Find and stop the other app**
   ```bash
   netstat -ano | findstr :5000
   ```

2. **Or change Flask port**
   Edit `app.py`, line 209:
   ```python
   app.run(host="127.0.0.1", port=5001, debug=False)
   ```
   
   Then update `popup.js`, line 5:
   ```javascript
   const BACKEND_URL = "http://127.0.0.1:5001";
   ```

---

### Error: "dataset.csv not found"

**Problem:** Dataset file missing

**Impact:** Backend may not start properly

**Solution:**
1. Verify file exists: `e:\CyberShield_Advanced_Full\dataset.csv`
2. If missing, restore from backup or source
3. File is needed for model accuracy calculation

---

## 🔍 Debugging Tips

### Check Browser Console
```
1. Click extension icon
2. Right-click on popup
3. Select "Inspect"
4. Go to "Console" tab
5. Look for error messages
```

### Check Flask Terminal
```
Look for:
- Python errors
- Request logs
- Exception traces
```

### Test Backend Manually
```bash
# Test health endpoint
curl http://127.0.0.1:5000/test

# Test prediction endpoint
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://google.com\"}"
```

### Verify Extension Files
```
extension/
├── manifest.json  ✓ Must exist
├── popup.html     ✓ Must exist
└── popup.js       ✓ Must exist
```

---

## 🆘 Still Having Issues?

### Quick Checklist
- [ ] Flask backend running
- [ ] Terminal shows "Running on http://127.0.0.1:5000"
- [ ] Extension loaded in Chrome
- [ ] Developer mode enabled
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Model file exists (modern_phishing_model.pkl)
- [ ] No firewall blocking port 5000
- [ ] Chrome console shows no errors

### Clean Restart
```bash
# 1. Stop Flask (Ctrl+C)
# 2. Reinstall dependencies
pip install -r requirements.txt --upgrade

# 3. Restart Flask
python app.py

# 4. Reload extension in Chrome
chrome://extensions/ → Click reload icon
```

---

## 📝 Error Log Template

If you need to report an issue, include:

```
**Error Message:**
[Copy exact error message]

**What I was doing:**
[Describe what you clicked/did]

**Browser Console:**
[Copy any red errors from console]

**Flask Terminal:**
[Copy any Python errors]

**Extension Version:**
v3.1

**Chrome Version:**
[Your Chrome version]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Error occurs]
```

---

**Most errors are fixed by:**
1. ✅ Restarting Flask backend
2. ✅ Reloading extension in Chrome
3. ✅ Checking backend is running on port 5000

**The float32 error you encountered is now FIXED! Just restart Flask.** 🎉
