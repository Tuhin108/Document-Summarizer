"""
Document Summarizer - Main Flask Application
Connects to Google Drive, parses documents, and generates AI summaries.
"""

import os
import io
import json
from flask import (
    Flask, render_template, redirect, url_for,
    session, request, send_file, flash, abort
)

from dotenv import load_dotenv


from drive_handler import DriveHandler
from document_parser import DocumentParser
from summarizer import Summarizer
from report_generator import ReportGenerator

load_dotenv()

app = Flask(__name__)

# ---- Security hardening ----
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "")
if not FLASK_SECRET_KEY or FLASK_SECRET_KEY.strip() == "change-this-in-production-secret-key":
    raise RuntimeError("FLASK_SECRET_KEY must be set to a strong random value in environment variables.")

app.secret_key = FLASK_SECRET_KEY

# Server-side session storage (prevents exposing OAuth tokens/client secrets to the browser cookie)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session")

# Ensure server-side sessions directory exists.
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.config["SESSION_PERMANENT"] = False

# Import after config so Pylance + runtime both see the dependency correctly.
from flask_session import Session
Session(app)



# Initialize components
drive = DriveHandler()
parser = DocumentParser()
ai_summarizer = Summarizer()
report_gen = ReportGenerator()


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    authenticated = "credentials" in session
    folder_id = session.get("folder_id", "")
    result_count = len(session.get("results", []))
    return render_template(
        "index.html",
        authenticated=authenticated,
        folder_id=folder_id,
        result_count=result_count
    )


@app.route("/auth")
def auth():
    """Initiate Google OAuth2 flow."""
    try:
        auth_url = drive.get_auth_url()
        return redirect(auth_url)
    except Exception as e:
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/oauth2callback")
def oauth2callback():
    """Handle OAuth2 callback from Google."""
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        flash(f"Google OAuth error: {error}", "error")
        return redirect(url_for("index"))

    if not code:
        flash("No authorization code received.", "error")
        return redirect(url_for("index"))

    try:
        credentials = drive.exchange_code(code)
        # Store credentials server-side in session (configured via Flask-Session).
        # Note: This still risks retaining refresh tokens; see security TODOs for a
        # production-grade solution (database/redis-backed session and token minimization).
        # Store OAuth credentials server-side only.
        # Credentials dict is already minimized (client_secret removed).
        session["credentials"] = credentials

        flash("Successfully connected to Google Drive!", "success")



    except Exception as e:
        flash(f"Failed to authenticate: {str(e)}", "error")


    return redirect(url_for("index"))


@app.route("/process", methods=["POST"])
def process():
    """Fetch documents from Drive, parse them, and summarize."""
    if "credentials" not in session:
        flash("Please connect to Google Drive first.", "error")
        return redirect(url_for("index"))

    folder_id = request.form.get("folder_id", "root").strip() or "root"
    session["folder_id"] = folder_id
    credentials = session["credentials"]

    try:
        files = drive.list_files(credentials, folder_id)
    except Exception as e:
        flash(f"Could not list files: {str(e)}", "error")
        return redirect(url_for("index"))

    if not files:
        flash("No supported documents (.pdf, .docx, .txt) found in that folder.", "warning")
        return redirect(url_for("index"))

    results = []
    for file_info in files:
        entry = {
            "filename": file_info["name"],
            "file_id": file_info["id"],
            "mime_type": file_info.get("mimeType", ""),
            "summary": "",
            "word_count": 0,
            "status": "ok",
        }
        try:
            content, mime_type = drive.download_file(
                credentials, file_info["id"], file_info["mimeType"]
            )
            text = parser.extract_text(content, mime_type, file_info["name"])

            if not text or not text.strip():
                entry["summary"] = "No readable text found in this document."
                entry["status"] = "warning"
            else:
                entry["word_count"] = len(text.split())
                entry["summary"] = ai_summarizer.summarize(text, file_info["name"])

        except Exception as e:
            entry["summary"] = f"Processing error: {str(e)}"
            entry["status"] = "error"

        results.append(entry)

    session["results"] = results
    flash(f"Processed {len(results)} document(s) successfully.", "success")
    return redirect(url_for("results"))


@app.route("/results")
def results():
    results_data = session.get("results", [])
    if not results_data:
        flash("No results yet. Process a folder first.", "warning")
        return redirect(url_for("index"))
    return render_template("results.html", results=results_data)


@app.route("/download/csv")
def download_csv():
    results_data = session.get("results", [])
    if not results_data:
        flash("Nothing to download.", "warning")
        return redirect(url_for("index"))

    csv_content = report_gen.generate_csv(results_data)
    return send_file(
        io.BytesIO(csv_content.encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="document_summaries.csv",
    )


@app.route("/download/pdf")
def download_pdf():
    results_data = session.get("results", [])
    if not results_data:
        flash("Nothing to download.", "warning")
        return redirect(url_for("index"))

    pdf_bytes = report_gen.generate_pdf(results_data)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="document_summaries.pdf",
    )


@app.route("/clear")
def clear():
    session.pop("results", None)
    session.pop("folder_id", None)
    flash("Results cleared.", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out from Google Drive.", "success")
    return redirect(url_for("index"))


# ──────────────────────────────────────────────
# Template helpers
# ──────────────────────────────────────────────

@app.template_filter("status_icon")
def status_icon(status):
    icons = {"ok": "✓", "warning": "⚠", "error": "✗"}
    return icons.get(status, "•")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("FLASK_DEBUG", "true").lower() == "true", port=port)
