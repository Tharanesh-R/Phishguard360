"""
Test the advanced phishing model API with various URLs.
"""
import requests
import json

API = "http://127.0.0.1:5000"

test_urls = [
    # Trusted domains (should be low risk: 2-8%)
    ("https://www.google.com", "Trusted - Google"),
    ("https://www.facebook.com/login", "Trusted - Facebook"),
    ("https://www.amazon.in/shopping", "Trusted - Amazon India"),
    ("https://github.com/user/repo", "Trusted - GitHub"),
    ("https://www.youtube.com/watch?v=abc", "Trusted - YouTube"),
    ("https://mail.google.com/inbox", "Trusted - Gmail"),
    ("https://www.wikipedia.org/wiki/Test", "Trusted - Wikipedia"),
    ("https://stackoverflow.com/questions", "Trusted - StackOverflow"),

    # Suspicious / Phishing (should be high risk: 40%+)
    ("http://192.168.1.1/login.php", "Phishing - IP Address"),
    ("http://google-login-verify.tk/account", "Phishing - Lookalike + suspicious TLD"),
    ("http://paypal-secure-update.xyz/verify", "Phishing - PayPal impersonation"),
    ("http://bit.ly/abc123", "Suspicious - URL shortener"),
    ("http://login-microsoft-update.click/password-reset", "Phishing - Microsoft impersonation"),
    ("http://free-prize-winner.club/urgent-click-here", "Phishing - Scam keywords"),
    ("https://some-unknown-site.com/page", "Unknown - generic site"),
    ("http://a.b.c.d.e.f.g.phish.com/login", "Phishing - excessive subdomains"),
]

print("=" * 80)
print("  CyberShield Advanced Model - URL Testing")
print("=" * 80)
print()

# Test backend health
try:
    r = requests.get(f"{API}/test", timeout=3)
    print(f"Backend: {r.text}")
except:
    print("ERROR: Backend not running! Start with: python app.py")
    exit(1)

# Test model info
try:
    r = requests.get(f"{API}/api/model_info", timeout=3)
    info = r.json()
    print(f"Model: {info.get('model_name', 'N/A')} | Accuracy: {info.get('accuracy', 'N/A')}% | F1: {info.get('f1_score', 'N/A')}%")
except:
    print("Could not get model info")

print()
print(f"{'URL':<55} {'Score':>6} {'Label':<20} {'Trust':<10}")
print("-" * 100)

for url, description in test_urls:
    try:
        r = requests.post(
            f"{API}/api/predict",
            json={"url": url},
            timeout=5
        )
        data = r.json()

        score = data.get("risk_score", "?")
        label = data.get("label", "?")
        trust = data.get("trust_status", "?")
        flags = data.get("flags", [])

        # Truncate URL for display
        display_url = url[:52] + "..." if len(url) > 55 else url

        print(f"{display_url:<55} {score:>5}% {label:<20} {trust:<10}")
        if flags:
            for f in flags:
                print(f"    ⚡ {f}")

    except Exception as e:
        print(f"{url[:55]:<55} ERROR: {e}")

print()
print("-" * 100)
print("Test complete!")
