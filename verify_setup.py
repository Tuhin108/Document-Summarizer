#!/usr/bin/env python3
"""
Verification script to check if the environment is set up correctly.
"""

import os
import sys
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11.9 or compatible."""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("   ✅ Python 3.11+ detected")
        return True
    else:
        print(f"   ❌ Python 3.11+ required (you have {version.major}.{version.minor})")
        return False

def check_credentials_file():
    """Check if credentials.json exists."""
    creds_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    print(f"\n📄 Checking for credentials file: {creds_file}")
    
    if os.path.exists(creds_file):
        print(f"   ✅ Found {creds_file}")
        try:
            with open(creds_file, 'r') as f:
                creds = json.load(f)
                if 'web' in creds or 'installed' in creds:
                    print("   ✅ Valid OAuth2 credentials format")
                    return True
                else:
                    print("   ❌ Invalid credentials format")
                    return False
        except Exception as e:
            print(f"   ❌ Error reading credentials: {e}")
            return False
    else:
        print(f"   ❌ {creds_file} not found in project root")
        print("      Download it from: https://console.cloud.google.com/")
        print("      APIs & Services → Credentials → OAuth 2.0 Client IDs")
        return False

def check_env_variables():
    """Check if required environment variables are set."""
    print("\n⚙️  Checking environment variables:")
    
    required_vars = {
        "FLASK_SECRET_KEY": "Flask session encryption key",
        "GOOGLE_CREDENTIALS_FILE": "Path to Google credentials JSON",
        "OAUTH_REDIRECT_URI": "OAuth redirect URI",
        "GEMINI_API_KEY": "Google Gemini API key",
        "GEMINI_MODEL": "Gemini model to use",
    }
    
    optional_vars = {
        "SUMMARY_MAX_TOKENS": "Max tokens per summary",
        "PORT": "Flask server port",
    }
    
    all_ok = True
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.environ.get(var, "").strip()
        if value and value != "your-very-secret-flask-key-here" and not value.startswith("http://") or var != "OAUTH_REDIRECT_URI":
            print(f"   ✅ {var}: Set")
            if var == "GEMINI_API_KEY" and value.startswith("AIza"):
                print(f"      └─ Starts with 'AIza' ✓")
        else:
            if not value:
                print(f"   ❌ {var}: NOT SET ({description})")
                all_ok = False
            else:
                print(f"   ⚠️  {var}: Default/placeholder value")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.environ.get(var, "").strip()
        if value:
            print(f"   ℹ️  {var}: {value} ({description})")
        else:
            print(f"   ℹ️  {var}: Using default")
    
    return all_ok

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies:")
    
    dependencies = {
        "flask": "Flask web framework",
        "dotenv": "Environment variable loader",
        "google.auth": "Google authentication",
        "google.generativeai": "Google Gemini API",
        "PyPDF2": "PDF processing (or PyMuPDF)",
        "docx": "DOCX processing",
    }
    
    all_installed = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"   ✅ {package}: Installed ({description})")
        except ImportError:
            print(f"   ❌ {package}: NOT INSTALLED ({description})")
            all_installed = False
    
    if not all_installed:
        print("\n   Install missing packages with:")
        print("   $ pip install -r requirements.txt")
    
    return all_installed

def main():
    """Run all checks."""
    print("=" * 60)
    print("Document Summarizer - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Credentials File", check_credentials_file()),
        ("Environment Variables", check_env_variables()),
        ("Dependencies", check_dependencies()),
    ]
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup complete! You can now run:")
        print("   $ python app.py")
        return 0
    else:
        print("\n⚠️  Please fix the issues above before running the app.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
