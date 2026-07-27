from flask_cors import CORS
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from collections import deque
import joblib
import numpy as np
import os
import re
import threading
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import imaplib
import email
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =============================
# INITIAL SETUP
# =============================

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = "cybershield_secret"

# =============================
# HEALTH CHECK (FOR EXTENSION)
# =============================

@app.route("/test")
def test():
    return "CyberShield backend running"

# =============================
# LOAD ADVANCED ML MODEL
# =============================

# Load the new advanced model trained on 88K+ phishing URLs
# Falls back to old model if new model is not available
if os.path.exists("cybershield_advanced_model.pkl"):
    model = joblib.load("cybershield_advanced_model.pkl")
    feature_names = joblib.load("model_feature_names.pkl")
    model_metadata = joblib.load("model_metadata.pkl")
    MODEL_TYPE = "advanced"
    MODEL_ACCURACY = model_metadata["accuracy"]
    print(f"[CyberShield] Advanced model loaded: {model_metadata['model_type']}")
    print(f"[CyberShield] Accuracy: {MODEL_ACCURACY}% | F1: {model_metadata['f1_score']}%")
else:
    model = joblib.load("modern_phishing_model.pkl")
    feature_names = None
    model_metadata = None
    MODEL_TYPE = "basic"
    MODEL_ACCURACY = 0
    print("[CyberShield] Basic model loaded (run train_model.py for advanced model)")

# =============================
# TRUSTED DOMAINS DATABASE
# =============================

TRUSTED_DOMAINS = {
    # Search Engines
    "google.com", "google.co.in", "google.co.uk", "google.co.jp",
    "google.com.br", "google.de", "google.fr", "google.es",
    "bing.com", "yahoo.com", "duckduckgo.com", "baidu.com",
    "yandex.ru", "yandex.com",

    # Social Media
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "pinterest.com", "reddit.com", "tumblr.com",
    "snapchat.com", "tiktok.com", "threads.net", "mastodon.social",
    "quora.com", "discord.com", "telegram.org",

    # Tech Giants
    "microsoft.com", "apple.com", "amazon.com", "amazon.in",
    "amazon.co.uk", "amazon.de", "amazon.co.jp",
    "netflix.com", "adobe.com", "oracle.com", "ibm.com",
    "salesforce.com", "cisco.com", "intel.com", "nvidia.com",
    "samsung.com", "huawei.com", "sony.com", "dell.com", "hp.com",
    "lenovo.com", "openai.com", "chatgpt.com",

    # Cloud & Dev Platforms
    "github.com", "gitlab.com", "bitbucket.org",
    "stackoverflow.com", "stackexchange.com",
    "aws.amazon.com", "azure.microsoft.com", "cloud.google.com",
    "heroku.com", "vercel.com", "netlify.com", "digitalocean.com",
    "cloudflare.com", "npmjs.com", "pypi.org", "docker.com",
    "kubernetes.io",

    # Email Providers
    "gmail.com", "outlook.com", "live.com", "hotmail.com",
    "protonmail.com", "proton.me", "zoho.com", "mail.yahoo.com",
    "icloud.com", "aol.com",

    # E-commerce & Payments
    "ebay.com", "etsy.com", "shopify.com", "walmart.com",
    "target.com", "bestbuy.com", "aliexpress.com", "alibaba.com",
    "flipkart.com", "myntra.com", "ajio.com",
    "paypal.com", "stripe.com", "razorpay.com", "paytm.com",

    # Banking & Finance
    "chase.com", "bankofamerica.com", "wellsfargo.com",
    "citibank.com", "hsbc.com", "barclays.com",
    "goldmansachs.com", "morganstanley.com",
    "sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "kotak.com", "yesbank.in",

    # Streaming & Entertainment
    "youtube.com", "spotify.com", "twitch.tv",
    "disneyplus.com", "hulu.com", "hbomax.com", "primevideo.com",
    "hotstar.com", "zee5.com", "sonyliv.com",
    "soundcloud.com", "vimeo.com",

    # Education
    "wikipedia.org", "wikimedia.org",
    "coursera.org", "udemy.com", "edx.org", "khanacademy.org",
    "mit.edu", "stanford.edu", "harvard.edu",
    "medium.com", "substack.com",
    "w3schools.com", "mozilla.org", "developer.mozilla.org",
    "freecodecamp.org",

    # News & Media
    "bbc.com", "bbc.co.uk", "cnn.com", "reuters.com",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "forbes.com", "bloomberg.com", "cnbc.com",
    "ndtv.com", "timesofindia.indiatimes.com", "thehindu.com",
    "hindustantimes.com",

    # Government
    "gov.in", "nic.in", "india.gov.in",
    "gov.uk", "usa.gov", "gov.au",
    "europa.eu", "un.org", "who.int",

    # Travel & Maps
    "booking.com", "airbnb.com", "tripadvisor.com",
    "expedia.com", "makemytrip.com", "goibibo.com",
    "maps.google.com", "waze.com",
    "uber.com", "lyft.com", "ola.com",

    # Communication
    "zoom.us", "teams.microsoft.com", "meet.google.com",
    "slack.com", "skype.com", "whatsapp.com", "signal.org",

    # Other Major Sites
    "archive.org", "dropbox.com", "box.com",
    "canva.com", "figma.com", "notion.so", "trello.com",
    "asana.com", "atlassian.com", "jira.atlassian.com",
    "wordpress.com", "wordpress.org", "wix.com", "squarespace.com",
    "godaddy.com", "namecheap.com",
    "craigslist.org", "yelp.com", "imdb.com",
    "roblox.com", "epicgames.com", "steam.com",
    "steampowered.com", "ea.com", "ubisoft.com",
}

# =============================
# KNOWN THREATS BLOCKLIST (FORTINET-STYLE)
# =============================

THREAT_CATEGORIES = {
    "phishing": "Phishing",
    "malware": "Malware",
    "scam": "Scam",
    "cryptomining": "Cryptomining",
    "c2": "Command & Control",
    "spam": "Spam",
    "adware": "Adware",
}

# Domain-based blocklist: domain -> category
BLOCKLIST_DB = {
    # ---- Phishing domains ----
    "login-verify-account.com": "phishing",
    "secure-banklogin.com": "phishing",
    "account-verify-now.com": "phishing",
    "update-your-account.net": "phishing",
    "paypal-security-update.com": "phishing",
    "appleid-verify.com": "phishing",
    "microsoft-login-verify.com": "phishing",
    "netflix-payment-update.com": "phishing",
    "amazon-security-alert.com": "phishing",
    "google-account-verify.net": "phishing",
    "facebook-security-check.com": "phishing",
    "instagram-verify-login.com": "phishing",
    "whatsapp-verify.com": "phishing",
    "linkedin-login-verify.com": "phishing",
    "twitter-account-verify.com": "phishing",
    "chase-online-verify.com": "phishing",
    "wellsfargo-security.com": "phishing",
    "bankofamerica-verify.com": "phishing",
    "citi-secure-login.com": "phishing",
    "hsbc-online-verify.com": "phishing",
    "dropbox-file-share.com": "phishing",
    "icloud-unlock-device.com": "phishing",
    "outlook-verify-email.com": "phishing",
    "dhl-tracking-update.com": "phishing",
    "fedex-delivery-notice.com": "phishing",
    "usps-package-track.com": "phishing",
    "irs-tax-refund.com": "phishing",
    "covid-test-result.com": "phishing",
    "social-security-update.com": "phishing",
    "verify-your-identity.net": "phishing",
    # ---- Malware domains ----
    "free-download-crack.com": "malware",
    "keygen-crack-download.com": "malware",
    "free-software-crack.net": "malware",
    "download-free-movies.xyz": "malware",
    "torrent-download-free.com": "malware",
    "hack-tool-download.com": "malware",
    "virus-scan-free.com": "malware",
    "antivirus-free-download.com": "malware",
    "pc-cleaner-free.com": "malware",
    "driver-update-free.com": "malware",
    "flash-player-update.com": "malware",
    "java-update-download.com": "malware",
    "browser-update-now.com": "malware",
    "system-alert-warning.com": "malware",
    "your-pc-is-infected.com": "malware",
    # ---- Scam domains ----
    "free-iphone-winner.com": "scam",
    "congratulations-winner.com": "scam",
    "you-won-prize.com": "scam",
    "claim-your-reward.net": "scam",
    "free-gift-card.com": "scam",
    "online-survey-reward.com": "scam",
    "earn-money-fast.com": "scam",
    "work-from-home-easy.com": "scam",
    "bitcoin-double.com": "scam",
    "crypto-giveaway-free.com": "scam",
    "investment-guaranteed.com": "scam",
    "forex-profit-daily.com": "scam",
    "lottery-winner-online.com": "scam",
    "lucky-draw-result.com": "scam",
    "dating-meet-now.com": "scam",
    # ---- Cryptomining domains ----
    "coinhive.com": "cryptomining",
    "coin-hive.com": "cryptomining",
    "crypto-loot.com": "cryptomining",
    "cryptoloot.pro": "cryptomining",
    "minero.cc": "cryptomining",
    "jsecoin.com": "cryptomining",
    "monerominer.rocks": "cryptomining",
    "webmine.pro": "cryptomining",
    "authedmine.com": "cryptomining",
    "ppoi.org": "cryptomining",
    # ---- C&C domains ----
    "evil-botnet-c2.com": "c2",
    "malware-control.net": "c2",
    "botnet-controller.com": "c2",
    "rat-server.com": "c2",
    "backdoor-access.net": "c2",
}

# Thread-safe lock for blocklist modifications
_blocklist_lock = threading.Lock()

# In-memory log of recently blocked URLs (thread-safe deque)
_blocked_log = deque(maxlen=100)
_blocked_log_lock = threading.Lock()

def add_to_blocked_log(url, domain, category, risk_score, flags):
    """Add a blocked URL entry to the in-memory log."""
    entry = {
        "url": url,
        "domain": domain,
        "category": THREAT_CATEGORIES.get(category, category),
        "risk_score": risk_score,
        "flags": flags[:5] if flags else [],
        "timestamp": datetime.now().isoformat(),
    }
    with _blocked_log_lock:
        _blocked_log.appendleft(entry)


def check_blocklist(url):
    """
    Check if a URL's domain is in the known-threats blocklist.
    Returns (is_blocked, category) tuple.
    """
    hostname = extract_domain(url)
    root = get_root_domain(hostname)

    with _blocklist_lock:
        # Check exact domain
        if hostname in BLOCKLIST_DB:
            return True, BLOCKLIST_DB[hostname]
        # Check root domain
        if root in BLOCKLIST_DB:
            return True, BLOCKLIST_DB[root]
        # Check if any blocklist domain is a parent
        for blocked_domain, cat in BLOCKLIST_DB.items():
            if hostname.endswith("." + blocked_domain):
                return True, cat

    return False, None


# =============================
# PHISHING INDICATOR KEYWORDS
# =============================

PHISHING_KEYWORDS = [
    "login", "signin", "sign-in", "log-in",
    "verify", "verification", "confirm", "confirmation",
    "secure", "security", "update", "upgrade",
    "account", "password", "credential",
    "suspend", "suspended", "restrict", "restricted",
    "expire", "expired", "expiring",
    "urgent", "immediately", "alert", "warning",
    "bank", "paypal", "wallet", "payment",
    "apple-id", "appleid",
    "microsoft-login", "outlook-verify",
    "free", "winner", "prize", "reward", "lucky",
    "click-here", "act-now",
]

COMMON_TLDS = {
    "com", "org", "net", "edu", "gov", "mil", "int",
    "co", "io", "me", "info", "biz", "name", "pro",
    "in", "uk", "us", "ca", "au", "de", "fr", "jp",
    "cn", "ru", "br", "it", "nl", "es", "se", "no",
    "fi", "dk", "at", "ch", "be", "pt", "pl", "cz",
    "tv", "cc", "ws", "la", "ly", "to", "fm", "am",
}

# =============================
# URL FEATURE EXTRACTOR
# =============================

def count_char(text, char):
    """Count occurrences of a character in text."""
    return text.count(char)

def count_vowels(text):
    """Count vowels in text."""
    return sum(1 for c in text.lower() if c in "aeiou")

def is_ip_address(hostname):
    """Check if hostname is an IP address."""
    ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return 1 if ip_pattern.match(hostname) else 0

def has_server_client(domain):
    """Check if domain contains 'server' or 'client' keywords."""
    lower = domain.lower()
    if "server" in lower or "client" in lower:
        return 1
    return 0

def extract_url_features(url):
    """
    Extract all 111 features from a URL string to match the
    dataset columns used for training the advanced phishing model.

    Returns a dict of feature_name -> value.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        parsed = urlparse("http://unknown.com")

    # URL components
    full_url = url
    hostname = (parsed.hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    domain = hostname
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""

    # Split path into directory and file
    path_parts = path.rsplit("/", 1)
    if len(path_parts) == 2:
        directory = path_parts[0]
        filename = path_parts[1]
    else:
        directory = path
        filename = ""

    # Parse query params
    params_str = query
    try:
        params_dict = parse_qs(query)
        num_params = len(params_dict)
    except Exception:
        num_params = 0

    # Check if TLD is present in params
    tld_in_params = 0
    for tld in COMMON_TLDS:
        if f".{tld}" in params_str.lower():
            tld_in_params = 1
            break

    # Check email in URL
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    email_in_url = 1 if email_pattern.search(full_url) else 0

    # Check if URL is shortened
    shorteners = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
                  "is.gd", "buff.ly", "adf.ly", "tiny.cc", "lnkd.in",
                  "rebrand.ly", "cutt.ly", "shorturl.at"}
    url_shortened = 1 if domain in shorteners else 0

    # Count TLD segments in URL
    tld_parts = domain.split(".")
    qty_tld = len(tld_parts) - 1 if len(tld_parts) > 1 else 0

    # Build feature dictionary matching all 111 columns
    special_chars = {
        "dot": ".", "hyphen": "-", "underline": "_",
        "slash": "/", "questionmark": "?", "equal": "=",
        "at": "@", "and": "&", "exclamation": "!",
        "space": " ", "tilde": "~", "comma": ",",
        "plus": "+", "asterisk": "*", "hashtag": "#",
        "dollar": "$", "percent": "%"
    }

    features = {}

    # ==== URL-level features (18 char counts + length + tld) ====
    for name, char in special_chars.items():
        features[f"qty_{name}_url"] = count_char(full_url, char)
    features["qty_tld_url"] = qty_tld
    features["length_url"] = len(full_url)

    # ==== Domain-level features ====
    for name, char in special_chars.items():
        key = f"qty_{name}_domain"
        if key in (feature_names or []):
            features[key] = count_char(domain, char)
    features["qty_vowels_domain"] = count_vowels(domain)
    features["domain_length"] = len(domain)
    features["domain_in_ip"] = is_ip_address(hostname)
    features["server_client_domain"] = has_server_client(domain)

    # ==== Directory-level features ====
    for name, char in special_chars.items():
        key = f"qty_{name}_directory"
        if key in (feature_names or []):
            features[key] = count_char(directory, char)
    features["directory_length"] = len(directory)

    # ==== File-level features ====
    for name, char in special_chars.items():
        key = f"qty_{name}_file"
        if key in (feature_names or []):
            features[key] = count_char(filename, char)
    features["file_length"] = len(filename)

    # ==== Params-level features ====
    for name, char in special_chars.items():
        key = f"qty_{name}_params"
        if key in (feature_names or []):
            features[key] = count_char(params_str, char)
    features["params_length"] = len(params_str)
    features["tld_present_params"] = tld_in_params
    features["qty_params"] = num_params

    # ==== Other URL-based features ====
    features["email_in_url"] = email_in_url
    features["url_shortened"] = url_shortened

    # ==== Network/DNS features (set to neutral defaults) ====
    # These need live DNS lookups; we use neutral values
    features["time_response"] = 0
    features["domain_spf"] = 0
    features["asn_ip"] = 0
    features["time_domain_activation"] = 0
    features["time_domain_expiration"] = 0
    features["qty_ip_resolved"] = 0
    features["qty_nameservers"] = 0
    features["qty_mx_servers"] = 0
    features["ttl_hostname"] = 0
    features["tls_ssl_certificate"] = 1 if full_url.startswith("https") else 0
    features["qty_redirects"] = 0
    features["url_google_index"] = 0
    features["domain_google_index"] = 0

    return features


def build_feature_vector(url):
    """
    Extract features from URL and return a properly ordered
    numpy array matching the model's expected input.
    """
    features_dict = extract_url_features(url)

    if feature_names:
        # Build vector in correct column order
        vector = []
        for fname in feature_names:
            vector.append(float(features_dict.get(fname, 0)))
        return np.array([vector], dtype=np.float32)
    else:
        # Fallback for old model
        length = len(url)
        has_https = 1 if url.startswith("https") else 0
        has_at = 1 if "@" in url else 0
        has_dash = 1 if "-" in url else 0
        dots = url.count(".")
        slashes = url.count("/")
        features = [length, has_https, has_at, has_dash, dots, slashes]
        while len(features) < model.n_features_in_:
            features.append(0)
        return np.array([features], dtype=np.float32)


# =============================
# DOMAIN HELPERS
# =============================

def extract_domain(url):
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        hostname = hostname.lower().strip()
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname
    except Exception:
        return ""

def get_root_domain(hostname):
    """Get root domain (e.g. 'mail.google.com' -> 'google.com')."""
    parts = hostname.split(".")
    if len(parts) >= 2:
        country_slds = {"co", "com", "org", "net", "ac", "gov", "edu", "gen", "res"}
        if len(parts) >= 3 and parts[-2] in country_slds and len(parts[-1]) <= 3:
            return ".".join(parts[-3:])
        return ".".join(parts[-2:])
    return hostname


# =============================
# SMART RISK ANALYSIS
# =============================

def analyze_url_risk(url):
    """
    Comprehensive URL risk analysis using the advanced ML model
    combined with trusted domain checking and heuristic analysis.
    """
    hostname = extract_domain(url)
    root_domain = get_root_domain(hostname)
    url_lower = url.lower()
    parsed = urlparse(url)

    # ----- Check trusted domains -----
    is_trusted = root_domain in TRUSTED_DOMAINS or hostname in TRUSTED_DOMAINS
    if not is_trusted:
        for td in TRUSTED_DOMAINS:
            if hostname.endswith("." + td):
                is_trusted = True
                break

    # ----- ML Model prediction -----
    feature_vector = build_feature_vector(url)
    ml_prob = float(model.predict_proba(feature_vector)[0][1])  # phishing probability

    # ----- Heuristic flags -----
    flags = []
    heuristic_boost = 0

    # IP address as hostname
    if is_ip_address(hostname):
        heuristic_boost += 15
        flags.append("IP address used instead of domain name")

    # No HTTPS
    if not url.startswith("https"):
        heuristic_boost += 5
        flags.append("No HTTPS encryption")

    # @ symbol
    if "@" in url:
        heuristic_boost += 15
        flags.append("Contains @ symbol (credential trick)")

    # Excessive subdomains
    subdomain_count = len(hostname.split("."))
    if subdomain_count > 4:
        heuristic_boost += 8
        flags.append(f"Excessive subdomains ({subdomain_count} levels)")

    # Very long URL
    if len(url) > 100:
        flags.append("Long URL")
    if len(url) > 200:
        heuristic_boost += 5
        flags.append("Extremely long URL")

    # Phishing keywords
    keyword_hits = sum(1 for kw in PHISHING_KEYWORDS if kw in url_lower)
    if keyword_hits >= 3:
        heuristic_boost += 10
        flags.append(f"Multiple phishing keywords ({keyword_hits})")
    elif keyword_hits >= 1:
        flags.append("Phishing keyword in URL")

    # Suspicious TLDs
    suspicious_tlds = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
                       ".buzz", ".club", ".work", ".click", ".link",
                       ".icu", ".cam", ".rest", ".surf"}
    for tld in suspicious_tlds:
        if hostname.endswith(tld):
            heuristic_boost += 8
            flags.append(f"Suspicious TLD: {tld}")
            break

    # Lookalike / Typosquatting
    lookalike_targets = {
        "google": "google.com", "facebook": "facebook.com",
        "microsoft": "microsoft.com", "apple": "apple.com",
        "amazon": "amazon.com", "netflix": "netflix.com",
        "paypal": "paypal.com", "instagram": "instagram.com",
        "twitter": "twitter.com", "linkedin": "linkedin.com",
        "whatsapp": "whatsapp.com", "youtube": "youtube.com",
    }
    for brand, real_domain in lookalike_targets.items():
        if brand in hostname and root_domain != real_domain:
            heuristic_boost += 15
            flags.append(f"Possible impersonation of {brand}")
            break

    # Encoded characters
    if url.count("%") > 3:
        heuristic_boost += 5
        flags.append("Excessive encoded characters")

    # Unusual port
    if parsed.port and parsed.port not in (80, 443):
        heuristic_boost += 5
        flags.append(f"Unusual port: {parsed.port}")

    # URL shortener
    shorteners = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
                  "is.gd", "buff.ly", "cutt.ly", "shorturl.at"}
    if hostname in shorteners:
        heuristic_boost += 5
        flags.append("URL shortener detected")

    # ----- Combine ML + Heuristic + Trust -----
    if is_trusted:
        # Trusted: ML score heavily dampened, base score very low
        base = 2.0
        # Small bump from minor heuristic flags (max +6)
        bump = min(heuristic_boost * 0.08, 6.0)
        risk_score = round(base + bump, 2)
        trust_status = "trusted"
    else:
        # Untrusted: ML model drives the score (70%) + heuristics (30%)
        ml_score = ml_prob * 100
        h_score = min(heuristic_boost, 50)
        raw = (ml_score * 0.70) + (h_score * 0.30)
        # Ensure minimum 12% for unknown domains
        risk_score = round(max(raw, 12.0), 2)
        risk_score = min(risk_score, 100.0)
        trust_status = "unknown"

    # ----- Label -----
    if risk_score > 70:
        label = "⚠️ Phishing"
    elif risk_score > 40:
        label = "⚠️ Suspicious"
    elif risk_score > 20:
        label = "🔶 Caution"
    else:
        label = "✅ Safe"

    return risk_score, label, trust_status, flags


# =============================
# ROUTES
# =============================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html", accuracy=round(MODEL_ACCURACY, 2))

@app.route("/analytics")
def analytics():
    import pandas as pd
    data = pd.read_csv("dataset.csv", nrows=5000, low_memory=True)
    label_column = data.columns[-1]

    if set(data[label_column].unique()).issubset({-1, 0, 1}):
        if -1 in data[label_column].values:
            data[label_column] = data[label_column].replace(-1, 0)

    counts = data[label_column].value_counts()

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Phishing vs Legitimate")
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.savefig("static/chart.png")
    plt.close()

    return render_template("analytics.html")

# =============================
# EMAIL SCAN HELPER
# =============================

def _extract_urls_from_text(text):
    """Extract all URLs from email body text."""
    url_pattern = re.compile(
        r'https?://[^\s<>"\')\]]+',
        re.IGNORECASE
    )
    return list(set(url_pattern.findall(text or "")))


def _get_email_body(msg):
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode(errors='ignore')
                except Exception:
                    pass
            elif content_type == "text/html":
                try:
                    html = part.get_payload(decode=True).decode(errors='ignore')
                    # Extract URLs from HTML links
                    href_pattern = re.compile(r'href=["\']([^"\'>]+)', re.IGNORECASE)
                    for match in href_pattern.findall(html):
                        if match.startswith('http'):
                            body += " " + match
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors='ignore')
        except Exception:
            pass
    return body


def _parse_email_date(date_str):
    """Parse email date string into a sortable datetime."""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime(2000, 1, 1)


def _scan_emails_core(scan_unseen_only=True, max_count=20, use_ml=True):
    """
    Core email scanning logic. Returns a list of email results.
    Each result includes subject, sender, date, risk score, label, url_count, and flags.
    Results are sorted newest-first.
    """
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    if not EMAIL_USER or not EMAIL_PASS:
        return None, "Email credentials missing in .env"

    results = []
    suspicious_keywords = [
        "urgent", "verify", "password", "bank",
        "otp", "login", "reset", "click", "account",
        "suspended", "security", "confirm", "expire",
        "immediately", "winner", "prize", "reward",
        "unauthorized", "alert", "update", "invoice",
    ]

    try:
        import socket
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=10)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox", readonly=True)

        # Search for UNSEEN (unread) or ALL
        search_criteria = "UNSEEN" if scan_unseen_only else "ALL"
        status, messages = mail.search(None, search_criteria)
        mail_ids = messages[0].split()

        # Take the most recent N emails
        target_ids = mail_ids[-max_count:] if len(mail_ids) > max_count else mail_ids

        for i in reversed(target_ids):  # newest first
            try:
                # Fetch full message for body URL extraction
                if use_ml:
                    status, msg_data = mail.fetch(i, "(BODY.PEEK[])")
                else:
                    status, msg_data = mail.fetch(i, "(BODY.PEEK[HEADER])")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg.get("Subject", "No Subject")
                        sender = msg.get("From", "Unknown Sender")
                        date_str = msg.get("Date", "Unknown Date")

                        # Decode subject if encoded
                        if subject:
                            from email.header import decode_header
                            decoded_parts = decode_header(subject)
                            subject = ""
                            for part, enc in decoded_parts:
                                if isinstance(part, bytes):
                                    subject += part.decode(enc or 'utf-8', errors='ignore')
                                else:
                                    subject += part

                        # Keyword-based scoring (subject)
                        keyword_hits = sum(
                            1 for word in suspicious_keywords
                            if word.lower() in (subject or "").lower()
                        )
                        keyword_score = min(keyword_hits * 20, 60)

                        # URL-based ML scoring (body)
                        urls_found = []
                        max_url_risk = 0
                        url_flags = []

                        if use_ml:
                            body = _get_email_body(msg)
                            urls_found = _extract_urls_from_text(body)

                            for url in urls_found[:10]:  # limit to 10 URLs per email
                                try:
                                    risk, label, trust, flags = analyze_url_risk(url)
                                    if risk > max_url_risk:
                                        max_url_risk = risk
                                    if flags:
                                        url_flags.extend(flags[:3])
                                except Exception:
                                    pass

                        # Combine keyword + URL ML scores
                        if urls_found and use_ml:
                            # 40% keyword, 60% ML URL analysis
                            combined_score = round(
                                keyword_score * 0.4 + max_url_risk * 0.6, 1
                            )
                        else:
                            combined_score = keyword_score

                        risk_score = min(combined_score, 100)

                        if risk_score >= 70:
                            label = "⚠️ High Risk"
                        elif risk_score >= 40:
                            label = "⚠️ Medium Risk"
                        else:
                            label = "✅ Low Risk"

                        results.append({
                            "subject": subject or "(No Subject)",
                            "sender": sender,
                            "date": date_str,
                            "risk": risk_score,
                            "label": label,
                            "url_count": len(urls_found),
                            "flags": list(set(url_flags))[:5],
                        })
            except Exception:
                continue

        mail.logout()

    except socket.timeout:
        return None, "Connection timed out — your network may be blocking IMAP port 993. Try a different network (e.g. mobile hotspot)."
    except imaplib.IMAP4.error as e:
        return None, f"IMAP authentication failed — check EMAIL_USER and EMAIL_PASS in .env. Details: {str(e)}"
    except (ConnectionRefusedError, OSError) as e:
        return None, f"Cannot reach imap.gmail.com — network may be blocking the connection. Error: {str(e)}"
    except Exception as e:
        return None, f"Error scanning email: {str(e)}"

    return results, None


# =============================
# EMAIL SCAN ROUTES
# =============================

@app.route("/manual_email_scan", methods=["GET", "POST"])
def manual_email_scan():

    if request.method == "POST":
        results, error = _scan_emails_core(scan_unseen_only=False, max_count=20, use_ml=True)

        if error:
            return error

        if results is None:
            results = []

        high_risk = sum(1 for r in results if r['risk'] >= 70)
        medium_risk = sum(1 for r in results if 40 <= r['risk'] < 70)
        low_risk = sum(1 for r in results if r['risk'] < 40)

        return render_template("email_results.html", results=results,
                               high_risk=high_risk, medium_risk=medium_risk, low_risk=low_risk)

    return render_template("manual_email_scan.html")


# =============================
# REAL-TIME EMAIL SCAN API
# =============================

@app.route("/api/email_scan")
def api_email_scan():
    """AJAX endpoint for real-time email scanning. Scans UNSEEN emails only."""
    try:
        results, error = _scan_emails_core(scan_unseen_only=True, max_count=30, use_ml=True)

        if error:
            return jsonify({"error": error, "results": [], "scan_time": datetime.now().isoformat()})

        if results is None:
            results = []

        high_risk = sum(1 for r in results if r['risk'] >= 70)
        medium_risk = sum(1 for r in results if 40 <= r['risk'] < 70)
        low_risk = sum(1 for r in results if r['risk'] < 40)

        return jsonify({
            "results": results,
            "total": len(results),
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "scan_time": datetime.now().isoformat(),
            "error": None
        })

    except Exception as e:
        return jsonify({"error": str(e), "results": [], "scan_time": datetime.now().isoformat()})

# =============================
# EXTENSION API (URL SCAN)
# =============================

@app.route("/api/predict", methods=["POST"])
def api_predict():

    try:
        req_data = request.get_json()

        if not req_data or "url" not in req_data:
            return jsonify({"error": "No URL received"})

        url = req_data["url"]

        # Skip non-scannable URLs
        if url.startswith("chrome://") or url.startswith("chrome-extension://"):
            return jsonify({
                "risk_score": 0.0,
                "label": "ℹ️ Browser Page",
                "trust_status": "browser",
                "domain": "chrome",
                "flags": [],
                "model_type": MODEL_TYPE,
                "model_accuracy": MODEL_ACCURACY
            })

        if url.startswith("about:") or url.startswith("edge://"):
            return jsonify({
                "risk_score": 0.0,
                "label": "ℹ️ Browser Page",
                "trust_status": "browser",
                "domain": "browser",
                "flags": [],
                "model_type": MODEL_TYPE,
                "model_accuracy": MODEL_ACCURACY
            })

        # Perform smart analysis using advanced model
        risk_score, label, trust_status, flags = analyze_url_risk(url)

        domain = extract_domain(url)

        return jsonify({
            "risk_score": risk_score,
            "label": label,
            "trust_status": trust_status,
            "domain": domain,
            "flags": flags,
            "model_type": MODEL_TYPE,
            "model_accuracy": MODEL_ACCURACY
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# =============================
# FORTINET-STYLE AUTO-BLOCK API
# =============================

@app.route("/api/check_block", methods=["POST"])
def api_check_block():
    """
    Fast-path endpoint for the extension to call during navigation.
    Combines blocklist lookup + ML prediction + heuristic analysis.
    Returns { block, category, risk_score, label, flags, domain }.
    """
    try:
        req_data = request.get_json()
        if not req_data or "url" not in req_data:
            return jsonify({"error": "No URL received", "block": False})

        url = req_data["url"]
        threshold = req_data.get("threshold", 50)

        # Skip browser internal pages
        if url.startswith(("chrome://", "chrome-extension://", "about:", "edge://", "brave://")):
            return jsonify({
                "block": False,
                "category": None,
                "risk_score": 0,
                "label": "Browser Page",
                "flags": [],
                "domain": "browser",
                "blocklist_hit": False
            })

        domain = extract_domain(url)

        # Step 1: Instant blocklist lookup
        is_blocked, block_category = check_blocklist(url)
        if is_blocked:
            category_label = THREAT_CATEGORIES.get(block_category, block_category)
            flags = [f"Known threat: {category_label}", "Domain found in threat database"]
            add_to_blocked_log(url, domain, block_category, 100, flags)
            return jsonify({
                "block": True,
                "category": category_label,
                "risk_score": 100,
                "label": f"🛡️ Blocked — {category_label}",
                "flags": flags,
                "domain": domain,
                "blocklist_hit": True
            })

        # Step 2: ML model + heuristic analysis
        risk_score, label, trust_status, flags = analyze_url_risk(url)

        should_block = risk_score >= threshold

        # Determine threat category from analysis
        category = None
        if should_block:
            if risk_score > 70:
                category = "Phishing"
            elif risk_score > 50:
                category = "Suspicious"
            else:
                category = "Caution"
            add_to_blocked_log(url, domain, category, risk_score, flags)

        return jsonify({
            "block": should_block,
            "category": category,
            "risk_score": risk_score,
            "label": label,
            "flags": flags,
            "domain": domain,
            "trust_status": trust_status,
            "blocklist_hit": False,
            "model_type": MODEL_TYPE,
            "model_accuracy": MODEL_ACCURACY
        })

    except Exception as e:
        return jsonify({"error": str(e), "block": False})


@app.route("/api/blocked_log")
def api_blocked_log():
    """Return the list of recently blocked URLs."""
    with _blocked_log_lock:
        log_list = list(_blocked_log)
    return jsonify({
        "blocked": log_list,
        "total": len(log_list)
    })


@app.route("/api/blocklist/add", methods=["POST"])
def api_blocklist_add():
    """Manually add a domain to the blocklist."""
    try:
        req_data = request.get_json()
        if not req_data or "domain" not in req_data:
            return jsonify({"error": "No domain provided", "success": False})

        domain = req_data["domain"].lower().strip()
        category = req_data.get("category", "phishing")

        if category not in THREAT_CATEGORIES:
            return jsonify({"error": f"Invalid category. Valid: {list(THREAT_CATEGORIES.keys())}", "success": False})

        with _blocklist_lock:
            BLOCKLIST_DB[domain] = category

        return jsonify({
            "success": True,
            "message": f"Added {domain} to blocklist as {THREAT_CATEGORIES[category]}",
            "total_blocked_domains": len(BLOCKLIST_DB)
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False})


@app.route("/api/blocklist/stats")
def api_blocklist_stats():
    """Return blocklist statistics."""
    with _blocklist_lock:
        category_counts = {}
        for cat in BLOCKLIST_DB.values():
            label = THREAT_CATEGORIES.get(cat, cat)
            category_counts[label] = category_counts.get(label, 0) + 1

    with _blocked_log_lock:
        recent_blocks = len(_blocked_log)

    return jsonify({
        "total_domains": len(BLOCKLIST_DB),
        "categories": category_counts,
        "recent_blocks": recent_blocks
    })

# =============================
# MODEL INFO API
# =============================

@app.route("/api/model_info")
def model_info():
    """Return information about the loaded ML model."""
    info = {
        "model_type": MODEL_TYPE,
        "accuracy": MODEL_ACCURACY,
        "status": "loaded"
    }
    if model_metadata:
        info.update({
            "model_name": model_metadata.get("model_type", "Unknown"),
            "precision": model_metadata.get("precision", 0),
            "recall": model_metadata.get("recall", 0),
            "f1_score": model_metadata.get("f1_score", 0),
            "n_features": model_metadata.get("n_features", 0),
            "training_samples": model_metadata.get("n_training_samples", 0),
            "top_features": model_metadata.get("top_features", [])[:10]
        })
    return jsonify(info)

# =============================
# RUN SERVER
# =============================

if __name__ == "__main__":
    print(f"[CyberShield] Starting server on http://127.0.0.1:5000")
    print(f"[CyberShield] Model: {MODEL_TYPE} | Accuracy: {MODEL_ACCURACY}%")
    print(f"[CyberShield] Blocklist: {len(BLOCKLIST_DB)} known threat domains loaded")
    print(f"[CyberShield] Fortinet-style auto-blocking ENABLED")
    app.run(host="127.0.0.1", port=5000, debug=False)
