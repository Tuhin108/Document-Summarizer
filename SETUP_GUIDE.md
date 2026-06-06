# Google OAuth2 Credentials Setup Guide

## Step-by-Step Instructions

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a Project** (top left)
3. Click **NEW PROJECT**
4. Enter a name (e.g., "Document Summarizer")
5. Click **CREATE**
6. Wait for the project to be created, then select it

### Step 2: Enable Google Drive API

1. In the Cloud Console, go to **APIs & Services → Library**
2. Search for "Google Drive API"
3. Click the result
4. Click **ENABLE**
5. Wait for the API to be enabled

### Step 3: Set Up OAuth2 Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Choose **External** (or Internal if using Workspace)
3. Click **CREATE**
4. Fill in the required fields:
   - **App name**: "Document Summarizer" (or your choice)
   - **User support email**: Your email address
   - **Developer contact email**: Your email address
5. Click **SAVE AND CONTINUE**
6. On the "Scopes" page, click **SAVE AND CONTINUE** (default scopes are fine)
7. On the "Test users" page:
   - Click **ADD USERS**
   - Add your Gmail address
   - Click **ADD**
8. Click **SAVE AND CONTINUE**
9. Review and click **BACK TO DASHBOARD**

### Step 4: Create OAuth2 Client Credentials

1. Go to **APIs & Services → Credentials**
2. Click **+ CREATE CREDENTIALS** (top left)
3. Select **OAuth 2.0 Client IDs**
4. If prompted, first click "Configure OAuth consent screen" and complete step 3
5. For **Application type**, choose **Web application**
6. Under **Authorized redirect URIs**, click **+ ADD URI**
7. Enter: `http://localhost:5000/oauth2callback`
8. Click **CREATE**
9. A popup will show your credentials. Click **DOWNLOAD** (downloads JSON file)

### Step 5: Save Credentials File

1. The downloaded file is named `<project_id>-<random_string>.json`
2. Rename it to: `credentials.json`
3. Move it to your project root folder (same folder as `app.py`)

Your file structure should look like:
```
document_summarizer/
├── app.py
├── summarizer.py
├── drive_handler.py
├── credentials.json          ← Your credentials file here
├── requirements.txt
└── .env
```

### Step 6: Set Environment Variables

1. Open or create `.env` file in the project root
2. Copy from `.env.example` if not already done:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and fill in:
   ```env
   FLASK_SECRET_KEY=your-random-secret-key
   GOOGLE_CREDENTIALS_FILE=credentials.json
   OAUTH_REDIRECT_URI=http://localhost:5000/oauth2callback
   GEMINI_API_KEY=AIza...your_gemini_api_key...
   GEMINI_MODEL=gemini-1.5-flash
   PORT=5000
   ```

### Step 7: Verify Setup

Run the verification script:
```bash
python verify_setup.py
```

This will check:
- ✅ Python 3.11.9 compatibility
- ✅ credentials.json exists
- ✅ Required dependencies installed
- ✅ Environment variables configured

### Step 8: Run the Application

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `credentials.json not found` | Ensure you downloaded the JSON file from Google Cloud and saved it as `credentials.json` in the project root |
| `GEMINI_API_KEY not set` | Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and add it to `.env` |
| `OAuth consent screen not configured` | Complete Step 3 above |
| `Permission denied` | Ensure your Google Cloud project has Drive API enabled (Step 2) |

---

## Security Reminders

⚠️ **IMPORTANT:**
- Never commit `credentials.json` to Git (it's in `.gitignore`)
- Never share your `GEMINI_API_KEY`
- Keep `.env` file secret
- The app uses read-only access to Drive - it cannot modify or delete files
