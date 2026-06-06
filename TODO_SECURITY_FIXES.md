# TODO_SECURITY_FIXES

## 1. Fix OAuth/session credential leakage (Critical)
- Stop storing Google OAuth credentials dict in Flask cookie session.
- Remove `client_secret` from anything stored in-session.
- Store only an opaque session identifier in Flask session, and keep actual credentials server-side (e.g., in-memory dict for now; optionally Redis).
- Alternatively, rework to use Flask-Session with server-side storage.

Files likely affected:
- app.py
- drive_handler.py

## 2. Enforce secure Flask secret key (Critical)
- Fail fast if `FLASK_SECRET_KEY` is missing or is the placeholder.
- Default `FLASK_DEBUG` to false.

Files likely affected:
- app.py

## 3. Add CSRF protection for POST /process (High)
- Add CSRF token and validate it on /process.

Files likely affected:
- app.py
- templates/index.html (to include token)

## 4. Add request/file processing limits (High)
- Cap number of files processed per request.
- Cap maximum extracted text characters/pages.
- Add time/size guardrails where feasible.

Files likely affected:
- app.py
- document_parser.py

## 5. Harden AI output before HTML/PDF (Medium)
- Ensure PDF rendering uses safe text (strip/escape characters that ReportLab might treat as markup).
- Add sanitization for AI summary strings.

Files likely affected:
- report_generator.py

## 6. Update README security notes (Low)
- Correct overstated privacy/security claims.

Files likely affected:
- README.md

