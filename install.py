"""
CyberShield — One-Time Installer
==================================
Run this ONCE to register the native messaging host with Chrome.
After this, the backend will auto-start when the extension loads.

Usage:
    python install.py

What it does:
1. Creates the native messaging manifest (com.cybershield.backend.json)
2. Registers it in Windows Registry for Chrome
3. Tests that everything works
"""

import os
import sys
import json
import winreg
import shutil

# =============================
# CONFIGURATION
# =============================

HOST_NAME = "com.cybershield.backend"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NATIVE_HOST_DIR = os.path.join(SCRIPT_DIR, "native_host")
HOST_BAT = os.path.join(NATIVE_HOST_DIR, "cybershield_host.bat")
MANIFEST_PATH = os.path.join(NATIVE_HOST_DIR, f"{HOST_NAME}.json")


def get_extension_id():
    """
    Ask the user for their Chrome extension ID.
    This is needed for the native messaging manifest.
    """
    print()
    print("=" * 60)
    print("  CyberShield — Auto-Start Installer")
    print("=" * 60)
    print()
    print("To complete setup, I need your Chrome extension ID.")
    print()
    print("How to find it:")
    print("  1. Open Chrome → chrome://extensions/")
    print("  2. Enable 'Developer mode' (top right)")
    print("  3. Find 'CyberShield' in the list")
    print("  4. Copy the ID (looks like: abcdefghijklmnopqrstuvwxyz)")
    print()

    ext_id = input("Paste your Extension ID: ").strip().lower()

    if not ext_id or len(ext_id) < 10:
        print("[ERROR] Invalid extension ID. Please try again.")
        sys.exit(1)

    return ext_id


def create_native_manifest(extension_id):
    """Create the Chrome native messaging host manifest JSON."""
    manifest = {
        "name": HOST_NAME,
        "description": "CyberShield Backend Auto-Start Host",
        "path": HOST_BAT,
        "type": "stdio",
        "allowed_origins": [
            f"chrome-extension://{extension_id}/"
        ]
    }

    os.makedirs(NATIVE_HOST_DIR, exist_ok=True)

    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"[OK] Created native messaging manifest: {MANIFEST_PATH}")
    return manifest


def register_in_registry():
    """Register the native messaging host in Windows Registry."""
    reg_key = f"SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\{HOST_NAME}"

    try:
        # Create registry key
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_key)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, MANIFEST_PATH)
        winreg.CloseKey(key)
        print(f"[OK] Registered in Windows Registry")
        print(f"     Key: HKCU\\{reg_key}")
        print(f"     Value: {MANIFEST_PATH}")

    except PermissionError:
        print("[ERROR] Cannot write to registry. Try running as Administrator.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Registry error: {e}")
        sys.exit(1)


def verify_setup():
    """Verify all files and registration are correct."""
    print()
    print("Verifying setup...")

    errors = []

    # Check host script
    host_py = os.path.join(NATIVE_HOST_DIR, "cybershield_host.py")
    if os.path.exists(host_py):
        print(f"  [OK] Host script: {host_py}")
    else:
        errors.append(f"Missing: {host_py}")

    # Check host batch launcher
    if os.path.exists(HOST_BAT):
        print(f"  [OK] Host launcher: {HOST_BAT}")
    else:
        errors.append(f"Missing: {HOST_BAT}")

    # Check manifest
    if os.path.exists(MANIFEST_PATH):
        print(f"  [OK] Manifest: {MANIFEST_PATH}")
    else:
        errors.append(f"Missing: {MANIFEST_PATH}")

    # Check app.py
    app_py = os.path.join(SCRIPT_DIR, "app.py")
    if os.path.exists(app_py):
        print(f"  [OK] Backend: {app_py}")
    else:
        errors.append(f"Missing: {app_py}")

    # Check registry
    try:
        reg_key = f"SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\{HOST_NAME}"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key)
        value, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if value == MANIFEST_PATH:
            print(f"  [OK] Registry: Correctly registered")
        else:
            errors.append(f"Registry value mismatch: {value} != {MANIFEST_PATH}")
    except FileNotFoundError:
        errors.append("Not found in Windows Registry")

    if errors:
        print()
        print("ERRORS:")
        for e in errors:
            print(f"  [FAIL] {e}")
        return False
    else:
        print()
        print("=" * 60)
        print("  ✅ Setup Complete!")
        print("=" * 60)
        print()
        print("The backend will now auto-start when you open Chrome")
        print("and the CyberShield extension loads.")
        print()
        print("No more manual startup needed!")
        print()
        return True


def main():
    # Check we're on Windows
    if sys.platform != "win32":
        print("[ERROR] This installer is for Windows only.")
        sys.exit(1)

    # Check Python version
    if sys.version_info < (3, 7):
        print("[ERROR] Python 3.7+ required.")
        sys.exit(1)

    # Get extension ID
    extension_id = get_extension_id()

    # Create manifest
    create_native_manifest(extension_id)

    # Register in registry
    register_in_registry()

    # Verify
    verify_setup()

    input("Press Enter to close...")


if __name__ == "__main__":
    main()
