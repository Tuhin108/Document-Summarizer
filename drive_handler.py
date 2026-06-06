"""
drive_handler.py — Google Drive OAuth2 Integration
Handles authentication, file listing, and file downloading.
"""

import os
import io
import json
import pickle
from typing import Any, Tuple, List, Dict, Optional


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Supported MIME types and their extensions
SUPPORTED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
    # Google Docs (exported as DOCX)
    "application/vnd.google-apps.document": ".docx",
}

# Google Docs export map
GOOGLE_EXPORT_MAP = {
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
}

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]


class DriveHandler:
    def __init__(self):
        self.credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.redirect_uri = os.environ.get(
            "OAUTH_REDIRECT_URI", "http://localhost:5000/oauth2callback"
        )

    # ────────────────────────────────────────────
    # Authentication
    # ────────────────────────────────────────────

    def get_auth_url(self) -> str:
        """Generate the Google OAuth2 authorization URL."""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Google OAuth2 credentials file not found: {self.credentials_file}\n"
                "Please follow these steps:\n"
                "1. Go to https://console.cloud.google.com/\n"
                "2. Create a new project or select an existing one\n"
                "3. Enable the Google Drive API (APIs & Services > Library)\n"
                "4. Go to APIs & Services > Credentials\n"
                "5. Create OAuth 2.0 Client IDs (Web application)\n"
                "6. Add redirect URI: http://localhost:5000/oauth2callback\n"
                "7. Download the JSON credentials file\n"
                "8. Save it as 'credentials.json' in the project root"
            )
        
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri,
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def exchange_code(self, code: str) -> dict:
        """Exchange auth code for credentials and return a serializable dict.

        SECURITY NOTE: The returned credentials dict must not include
        `client_secret` (avoid persisting sensitive OAuth client material).
        """

        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Google OAuth2 credentials file not found: {self.credentials_file}"
            )
        
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        return self._creds_to_dict(creds)

    def _creds_to_dict(self, creds: Any) -> dict:

        # IMPORTANT: Do not persist client_secret in any session/storage that
        # might be exposed to the user. OAuth web apps typically only need the
        # access/refresh tokens plus token URI + client id to refresh.
        return {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "scopes": list(creds.scopes) if creds.scopes else SCOPES,
        }


    def _get_service(self, credentials_dict: dict):
        """Reconstruct credentials and build Drive service."""
        # Note: client_secret is only required for certain OAuth flows.
        # For installed/web flows already authorized, refresh can work
        # without persisting client_secret in application storage.
        creds = Credentials(
            token=credentials_dict["token"],
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict["token_uri"],
            client_id=credentials_dict["client_id"],
            client_secret=credentials_dict.get("client_secret"),
            scopes=credentials_dict.get("scopes", SCOPES),
        )


        # Auto-refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build("drive", "v3", credentials=creds)

    # ────────────────────────────────────────────
    # File Operations
    # ────────────────────────────────────────────

    def list_files(self, credentials_dict: dict, folder_id: str = "root") -> List[Dict]:
        """
        List all supported documents in the given Google Drive folder.
        Returns a list of {id, name, mimeType} dicts.
        """
        service = self._get_service(credentials_dict)

        # Build MIME type query
        mime_conditions = " or ".join(
            [f"mimeType='{m}'" for m in SUPPORTED_MIME_TYPES.keys()]
        )
        query = (
            f"'{folder_id}' in parents "
            f"and ({mime_conditions}) "
            f"and trashed=false"
        )

        results = []
        page_token = None

        while True:
            response = (
                service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)",
                    pageToken=page_token,
                    orderBy="name",
                )
                .execute()
            )

            results.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        return results

    def download_file(
        self, credentials_dict: dict, file_id: str, mime_type: str
    ) -> Tuple[bytes, str]:
        """
        Download a file from Google Drive.
        For Google Docs, exports to DOCX.
        Returns (file_bytes, actual_mime_type).
        """
        service = self._get_service(credentials_dict)
        buffer = io.BytesIO()

        if mime_type in GOOGLE_EXPORT_MAP:
            # Export Google Workspace files
            export_mime, _ = GOOGLE_EXPORT_MAP[mime_type]
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            actual_mime = export_mime
        else:
            request = service.files().get_media(fileId=file_id)
            actual_mime = mime_type

        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue(), actual_mime

    def get_folder_name(self, credentials_dict: dict, folder_id: str) -> Optional[str]:
        """Get the display name of a folder."""
        if folder_id == "root":
            return "My Drive (root)"
        try:
            service = self._get_service(credentials_dict)
            file_meta = (
                service.files()
                .get(fileId=folder_id, fields="name")
                .execute()
            )
            return file_meta.get("name", folder_id)
        except Exception:
            return folder_id
