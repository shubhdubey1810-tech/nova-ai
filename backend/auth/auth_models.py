"""
NØVA AI 1.0
Authentication Models

Pydantic models used by the authentication system.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class GoogleUser(BaseModel):
    """
    User information returned by Google.
    """

    google_id: str = Field(..., min_length=1)
    email: EmailStr
    name: str = Field(..., min_length=1)
    picture: Optional[str] = None
    email_verified: bool = False


class UserSession(BaseModel):
    """
    Represents an authenticated NØVA user session.
    """

    user_id: str
    google_id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    authenticated: bool = True


class LoginResponse(BaseModel):
    """
    Response returned after successful authentication.
    """

    success: bool
    message: str
    user: Optional[GoogleUser] = None


class LogoutResponse(BaseModel):
    """
    Response returned after logout.
    """

    success: bool
    message: str


class AuthStatus(BaseModel):
    """
    Current authentication status.
    """

    authenticated: bool
    user: Optional[GoogleUser] = None