"""
NØVA AI
Google Authentication Routes
"""

from fastapi import APIRouter, Request
from fastapi.responses import (
    JSONResponse,
    RedirectResponse
)

from .google_auth import google_auth


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/google/login")
def google_login(
    request: Request
):

    try:

        authorization_url, state = (
            google_auth.start()
        )

        request.session[
            "oauth_state"
        ] = state

        return RedirectResponse(
            authorization_url,
            status_code=302
        )

    except Exception as error:

        return JSONResponse(
            status_code=500,

            content={
                "success": False,

                "message":
                    "Could not start Google authentication.",

                "error":
                    str(error)
            }
        )


@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):

    if error:

        return JSONResponse(
            status_code=400,

            content={
                "success": False,

                "message":
                    f"Google login failed: {error}"
            }
        )

    saved_state = request.session.get(
        "oauth_state"
    )

    if not state or state != saved_state:

        return JSONResponse(
            status_code=400,

            content={
                "success": False,

                "message":
                    "Invalid OAuth state. "
                    "Please start Google login again."
            }
        )

    if not code:

        return JSONResponse(
            status_code=400,

            content={
                "success": False,

                "message":
                    "Authorization code was not provided."
            }
        )

    try:

        token = google_auth.exchange_code(
            code
        )

        profile = (
            google_auth.get_user_info(
                token["access_token"]
            )
        )

        request.session[
            "authenticated"
        ] = True

        request.session[
            "nova_user"
        ] = {

            "user_id":
                str(profile["sub"]),

            "google_id":
                str(profile["sub"]),

            "name":
                profile.get(
                    "name"
                ) or profile["email"],

            "email":
                profile["email"],

            "picture":
                profile.get("picture"),

            "email_verified":
                bool(
                    profile.get(
                        "email_verified",
                        False
                    )
                ),
        }

        # Clear OAuth state only after success.
        request.session.pop(
            "oauth_state",
            None
        )

        return RedirectResponse(
            url="/",
            status_code=302
        )

    except Exception as error:

        # Keep the error visible during testing.
        return JSONResponse(
            status_code=500,

            content={
                "success": False,

                "message":
                    "Google authentication failed.",

                "error":
                    str(error)
            }
        )


@router.get("/status")
def auth_status(
    request: Request
):

    user = request.session.get(
        "nova_user"
    )

    authenticated = bool(
        request.session.get(
            "authenticated"
        )
        and user
    )

    return {
        "authenticated":
            authenticated,

        "user":
            user if authenticated
            else None
    }


@router.post("/logout")
def logout(
    request: Request
):

    request.session.clear()

    return {
        "success": True,

        "message":
            "Logged out successfully.",

        "authenticated":
            False
    }