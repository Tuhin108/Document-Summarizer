# SECURITY_PATCH_PLAN.md

## Information gathered
- `app.py` currently uses Flask-Session filesystem, but still stores `session["credentials"]` in the session.
- `templates/index.html` submits `folder_id` to `/process` with no CSRF token.
- `app.py` `POST /process` has no CSRF validation and no request/file processing limits.
- `drive_handler.py` serializes OAuth tokens plus `client_secret` into a credentials dict.
- `summarizer.py` uses `system_instruction=...` when creating `GenerativeModel` (this also triggered Pylance type errors).
- `report_generator.py` inserts AI summaries into ReportLab `Paragraph` objects without sanitizing ReportLab markup control characters.

## Edit plan (file-by-file)

### 1) `drive_handler.py`
- Add a minimal credentials storage method that **does not include** `client_secret` in the serialized dict.
- Store only: `token`, `refresh_token`, `token_uri`, `client_id`, `scopes`.
- Ensure `_get_service` can reconstruct Credentials without `client_secret`.
- Add server-side session helpers: either
  - keep the serialized credentials, but ensure they never end up client-visible (server-side session only), OR
  - store credentials in an in-memory server-side cache keyed by a random session id.

### 2) `app.py`
- Enforce secure defaults:
  - remove debug default-to-true behavior (`FLASK_DEBUG` default false)
- Add CSRF protection:
  - generate token in `index()` and store in session
  - embed hidden input in `templates/index.html`
  - validate token in `POST /process`
- Add strict request limits:
  - `MAX_FILES_PER_REQUEST`
  - `MAX_EXTRACTED_CHARS_PER_DOC` (parser already has `MAX_CHARS`, but cap further if needed)
  - `MAX_TOTAL_CHARS_REQUEST`
- Add output sanitization before PDF export:
  - sanitize summary text for ReportLab `Paragraph` usage.
- Remove any unnecessary sensitive values from the session.

### 3) `templates/index.html`
- Add hidden CSRF input inside the `<form>`:
  - `<input type="hidden" name="csrf_token" value="{{ csrf_token }}" />`

### 4) `report_generator.py`
- Sanitize AI summary and filename strings before passing into ReportLab `Paragraph`.
  - ReportLab `Paragraph` treats a subset of markup; remove/escape characters/sequences that trigger it (e.g., `<`, `&`, `>` or ReportLab-specific tags).
  - Also normalize whitespace and strip control characters.

### 5) `README.md`
- Correct security/privacy claims:
  - update “No data storage” section to be accurate about server-side session storage.
  - document that credentials are stored server-side (filesystem session) and cleared on logout.

## Followup steps after patch
- Run `python -m py_compile *.py`.
- Start app locally and verify flow:
  1) /auth redirect
  2) /oauth2callback returns success
  3) /process rejects missing/invalid CSRF
  4) /process works with valid CSRF
  5) /download/csv and /download/pdf succeed

## Approval request
- Proceed with applying the above patch plan.

