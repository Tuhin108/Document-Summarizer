# DocSummarizer

AI-powered document summarization via Google Drive Integration.  
Connect → Select Folder → Get Summaries → Export PDF/CSV.

[![Python](https://img.shields.io/badge/Python-3.11.9-blue?style=flat-square)](https://www.python.org/downloads/release/python-3119/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=flat-square)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini%203.5-orange?style=flat-square)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](LICENSE)

---

## 📋 Features

| Feature | Details |
|---------|---------|
| **Google Drive OAuth2** | Secure read-only access to Google Drive files |
| **Multi-Format Support** | PDF, DOCX, DOCX (Google Docs), TXT, Markdown, CSV |
| **AI Summaries** | 5–10 sentence professional summaries via Gemini API |
| **Web UI** | Dark editorial design, fully responsive, real-time processing |
| **Export Options** | Download results as styled PDF or CSV |
| **No Data Storage** | OAuth credentials stored in session only, not persisted |

---

## 🏗️ Architecture

```
document_summarizer/
├── app.py                    # Flask application & routing
├── drive_handler.py          # Google Drive OAuth2 & API integration
├── document_parser.py        # Text extraction (PDF/DOCX/TXT/CSV/MD)
├── summarizer.py             # Google Gemini API summarization engine
├── report_generator.py       # PDF/CSV report generation (ReportLab)
├── templates/
│   ├── base.html             # Base layout with navigation
│   ├── index.html            # Home page (connect + process)
│   └── results.html          # Results table with export options
├── static/
│   ├── css/style.css         # Dark theme styling
│   └── js/main.js            # UI interactions & loading states
├── requirements.txt          # Python dependencies
├── .env                       # Environment variables (NOT in repo)
├── .python-version           # Python 3.11.9 specification
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11.9+** ([Download](https://www.python.org/downloads/release/python-3119/))
- **Google Cloud Account** (free tier available)
- **Gemini API Key** (free tier: 60 requests/minute)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/document-summarizer.git
cd document_summarizer
```

### 2️⃣ Create Virtual Environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Get Google Credentials

**Follow the detailed setup guide in [SETUP_GUIDE.md](SETUP_GUIDE.md)**, which covers:

1. Creating a Google Cloud Project
2. Enabling the Google Drive API
3. Configuring OAuth2 Consent Screen
4. Downloading credentials.json
5. Setting up environment variables

**Quick Summary:**
- Download `credentials.json` from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- Save in project root directory
- Set `GOOGLE_CREDENTIALS_FILE=credentials.json` in `.env`

### 5️⃣ Configure Environment

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
# Flask
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_DEBUG=true

# Google OAuth2
GOOGLE_CREDENTIALS_FILE=credentials.json
OAUTH_REDIRECT_URI=http://localhost:5000/oauth2callback

# Google Gemini API
GEMINI_API_KEY=AIza...your-api-key-here
GEMINI_MODEL=gemini-3.5-flash

# Summarization
SUMMARY_MAX_TOKENS=3000

# Server
PORT=5000
```

**Getting API Keys:**
- **Google Drive API**: Enabled via Google Cloud Console (free)
- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey) (free, 60 req/min)

### 6️⃣ Run Application

```bash
python app.py
```

Visit: **[http://localhost:5000](http://localhost:5000)**

---

## 📖 Usage

### Step 1: Connect to Google Drive

Click **"Connect to Google Drive"** → Authorize app → Grant read-only Drive access

### Step 2: Select Folder

Enter a Google Drive folder ID or use "root" for your main Drive folder

**How to get folder ID:**
- Navigate to folder in Google Drive
- URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`
- Copy the ID

### Step 3: Process Documents

Click **"Process Folder"** → App fetches and summarizes all supported files

**Supported formats:**
- `.pdf` — PDFs (PyMuPDF)
- `.docx` — Word documents (python-docx)
- `.doc` — Legacy Word docs (parsed as DOCX)
- `.txt` — Plain text files
- `.md` — Markdown files
- `.csv` — CSV tables
- Google Docs — Auto-converted to DOCX

### Step 4: View & Export

**View Results:**
- Summaries displayed in results table
- Click "Show less ▲" to collapse long summaries

**Download:**
- **CSV**: Comma-separated, spreadsheet-compatible
- **PDF**: Styled report with company branding, page breaks for long document sets

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_SECRET_KEY` | *(required)* | Random key for session encryption |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (development only) |
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | Path to OAuth2 credentials JSON |
| `OAUTH_REDIRECT_URI` | `http://localhost:5000/oauth2callback` | OAuth2 callback URL (must match Google Cloud config) |
| `GEMINI_API_KEY` | *(required)* | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Gemini model to use (latest/fastest) |
| `SUMMARY_MAX_TOKENS` | `3000` | Max tokens per summary (higher = longer output) |
| `PORT` | `5000` | Server port |

### API Models Available

```
✓ gemini-3.5-flash        (Latest, fastest, cheapest)
✓ gemini-3.1-flash-lite   (Lightweight)
✓ gemini-2.5-flash        (Stable, proven)
✓ gemini-2.5-pro          (More capable, slower)
✓ gemini-2.0-flash        (Earlier generation)
```

**Recommendation:** Use `gemini-3.5-flash` for best price/performance.

---

## 🔐 Security & Privacy

### What Gets Sent to Google

1. **Google Drive OAuth**: Only your authentication token (read-only access)
2. **Document Text**: Sent to Gemini API for summarization (not stored by Google)
3. **No Data Persistence**: Credentials stored in Flask session only, cleared on logout

### What NEVER Gets Committed

These files contain secrets and are in `.gitignore`:

```
.env                    # API keys, GEMINI_API_KEY, etc.
credentials.json        # OAuth2 credentials
token.pickle            # Session tokens
.vscode/               # IDE settings
__pycache__/           # Python bytecode
*.log                  # Log files
```

### Running Locally

All data stays on your local machine. No cloud storage or logging.

---

## 📦 Dependencies

**Core Dependencies:**
- `flask==3.0+` — Web framework
- `google-auth-oauthlib` — OAuth2 authentication
- `google-auth-httplib2` — Google API client
- `googleapiclient` — Google Drive API
- `google-generativeai==0.4.1` — Gemini API client
- `python-docx` — DOCX parsing
- `PyMuPDF` — PDF text extraction
- `reportlab` — PDF report generation
- `python-dotenv` — Environment variable management

See [requirements.txt](requirements.txt) for exact versions.

---

## 🐛 Troubleshooting

### "credentials.json not found"
- Download from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- Save to project root as `credentials.json`
- Ensure `GOOGLE_CREDENTIALS_FILE=credentials.json` in `.env`

### "GEMINI_API_KEY not set"
- Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Add to `.env`: `GEMINI_API_KEY=AIza...`

### "Access denied by OAuth"
- Ensure your Google account is added as a **test user** in Google Cloud Console
- Navigate to: APIs & Services → OAuth consent screen → Test users → Add your email

### "Summaries are too short / truncated"
- Increase `SUMMARY_MAX_TOKENS` in `.env` (default: 3000)
- Try: `SUMMARY_MAX_TOKENS=4000` or higher

### "Process is slow"
- Use `gemini-3.5-flash` (fastest model)
- Reduce number of files being processed
- Process smaller folders instead of entire Drive

### "PDF export fails"
- Ensure `reportlab` is installed: `pip install reportlab`
- Check disk space for temporary files

---

## 🚀 Deployment

### Production Deployment

⚠️ **NOT RECOMMENDED** for production without:

1. **WSGI Server** (Gunicorn, uWSGI, Waitress)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **SSL/HTTPS** (use nginx + Let's Encrypt)

3. **Environment Secrets Management**
   - Use managed secrets (AWS Secrets Manager, Azure Key Vault)
   - NEVER commit `.env` files

4. **Database for Sessions** (Redis, PostgreSQL)
   - Current: Flask in-memory sessions only

5. **Rate Limiting**
   - Add API rate limiters to prevent abuse

6. **Monitoring & Logging**
   - Add structured logging
   - Monitor API quota usage

---

## 📝 Development

### Running Tests

```bash
# Check syntax
python -m py_compile *.py

# Test summarizer directly
python -c "from summarizer import Summarizer; s = Summarizer(); print(s.summarize('Your text here'))"
```

### Adding Features

1. **New Document Format**: Extend `document_parser.py`
2. **Different AI Provider**: Implement in `summarizer.py` as new method
3. **Export Format**: Add generator to `report_generator.py`

### Code Structure

- **Stateless routes** in `app.py` — use Flask sessions for state
- **OAuth credentials** refreshed per request via `drive_handler.py`
- **Error handling** with Flask flash messages for user feedback
- **Type hints** throughout for IDE support and documentation

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file

---

## 👤 Author

Document Summarizer v1.0 (June 2026)

**Contact:** [Your Email] | **GitHub:** [Your GitHub]

---

## 🙏 Acknowledgments

- **Google APIs** for Drive, OAuth2, and Gemini
- **ReportLab** for PDF generation
- **Flask** ecosystem
- Inspired by document analysis workflows

---

## 📞 Support

For issues, questions, or suggestions:

1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
2. Review **Troubleshooting** section above
3. Check [GitHub Issues](https://github.com/YOUR_USERNAME/document-summarizer/issues)
4. Create a new issue with:
   - Error message (full traceback)
   - Steps to reproduce
   - Python version (`python --version`)
   - OS (Windows/Mac/Linux)

---

## 🔄 Version History

### v1.0 (June 2026)
- ✅ Google Drive OAuth2 integration
- ✅ Multi-format document parsing
- ✅ Gemini API summarization
- ✅ Web UI with PDF/CSV export
- ✅ Responsive dark theme
- ✅ Python 3.11.9 support

### Recent Fixes (June 2026)
- Fixed Gemini model compatibility (v1.5 → v3.5)
- Increased token limit (1500 → 3000) for complete summaries
- Added truncation detection & response cleaning
- Enhanced error logging for debugging

---

**Made with ❤️ using Flask + Google APIs + Gemini AI**
#
