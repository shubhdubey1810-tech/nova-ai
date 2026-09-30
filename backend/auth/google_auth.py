"""
NØVA AI
Google OAuth 2.0 for local web development
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]

CLIENT_SECRETS_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRETS",
    str(BASE_DIR / "client_secret.json")
)

GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://127.0.0.1:8000/auth/google/callback"
)

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
USERINFO_URI = (
    "https://openidconnect.googleapis.com/v1/userinfo"
)

SCOPES = [
    "openid",
    "email",
    "profile",
]


class GoogleAuth:

    def __init__(self) -> None:
        self.client_secrets_file = CLIENT_SECRETS_FILE
        self.redirect_uri = GOOGLE_REDIRECT_URI

        self.client_id, self.client_secret = (
            self._load_client()
        )

    def _load_client(self) -> tuple[str, str]:

        path = Path(
            self.client_secrets_file
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Google OAuth credentials not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        web = (
            data.get("web")
            or data.get("installed")
        )

        if not web:

            raise RuntimeError(
                "client_secret.json does not contain "
                "a web or installed OAuth client."
            )

        client_id = web.get(
            "client_id"
        )

        client_secret = web.get(
            "client_secret"
        )

        if not client_id:

            raise RuntimeError(
                "Google client_id is missing."
            )

        if not client_secret:

            raise RuntimeError(
                "Google client_secret is missing."
            )

        return (
            str(client_id),
            str(client_secret)
        )

    def start(self) -> tuple[str, str]:

        import secrets

        state = secrets.token_urlsafe(
            32
        )

        params = {
            "client_id":
                self.client_id,

            "redirect_uri":
                self.redirect_uri,

            "response_type":
                "code",

            "scope":
                " ".join(SCOPES),

            "state":
                state,

            "access_type":
                "offline",

            "prompt":
                "select_account",
        }

        authorization_url = (
            f"{AUTH_URI}?"
            f"{urllib.parse.urlencode(params)}"
        )

        return (
            authorization_url,
            state
        )

    def exchange_code(
        self,
        code: str
    ) -> dict[str, Any]:

        payload = urllib.parse.urlencode({
            "code":
                code,

            "client_id":
                self.client_id,

            "client_secret":
                self.client_secret,

            "redirect_uri":
                self.redirect_uri,

            "grant_type":
                "authorization_code",
        }).encode(
            "utf-8"
        )

        request = urllib.request.Request(
            TOKEN_URI,

            data=payload,

            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded",

                "Accept":
                    "application/json",
            },

            method="POST",
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=20
            ) as response:

                result = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

        except urllib.error.HTTPError as error:

            body = error.read().decode(
                "utf-8",
                errors="replace"
            )

            raise RuntimeError(
                "Google token exchange failed "
                f"(HTTP {error.code}): {body}"
            ) from error

        except urllib.error.URLError as error:

            raise RuntimeError(
                "Could not connect to Google token server: "
                f"{error.reason}"
            ) from error

        if not result.get(
            "access_token"
        ):

            raise RuntimeError(
                "Google did not return an access token: "
                f"{result}"
            )

        return result

    def get_user_info(
        self,
        access_token: str
    ) -> dict[str, Any]:

        request = urllib.request.Request(
            USERINFO_URI,

            headers={
                "Authorization":
                    f"Bearer {access_token}",

                "Accept":
                    "application/json",
            },

            method="GET",
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

        except urllib.error.HTTPError as error:

            body = error.read().decode(
                "utf-8",
                errors="replace"
            )

            raise RuntimeError(
                "Google userinfo request failed "
                f"(HTTP {error.code}): {body}"
            ) from error

        if not data.get(
            "sub"
        ) or not data.get(
            "email"
        ):

            raise RuntimeError(
                "Google returned incomplete user information."
            )

        return data


google_auth = GoogleAuth()