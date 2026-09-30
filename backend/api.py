"""
NØVA AI API
"""

from pathlib import Path
import os
import secrets

from fastapi import (
    FastAPI,
    HTTPException,
    Request
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from starlette.middleware.sessions import (
    SessionMiddleware
)

from .universal_ai_engine import nova_universal_ai
from .auth.auth_routes import router as auth_router
from .memory import nova_memory
from .services.chat_service import chat_service

# --------------------------------------------
# Paths
# --------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = FRONTEND_DIR / "index.html"

# --------------------------------------------
# App
# --------------------------------------------

app = FastAPI(
    title="NØVA AI 1.0 API",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static"
)

app.mount(
    "/downloads",
    StaticFiles(directory=str(DOWNLOADS_DIR)),
    name="downloads"
)

# --------------------------------------------
# Session
# --------------------------------------------

SESSION_SECRET = os.getenv(
    "NOVA_SESSION_SECRET"
)

if not SESSION_SECRET:
    SESSION_SECRET = secrets.token_urlsafe(32)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False,
)

# --------------------------------------------
# CORS
# --------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------
# Auth
# --------------------------------------------

app.include_router(
    auth_router
)

# --------------------------------------------
# Models
# --------------------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ConversationCreate(BaseModel):
    title: str = "New Chat"

# --------------------------------------------
# Authentication Helper
# --------------------------------------------

def get_current_user(
    request: Request
):

    authenticated = request.session.get(
        "authenticated",
        False
    )

    user = request.session.get(
        "nova_user"
    )

    if not authenticated or not user:

        raise HTTPException(
            status_code=401,
            detail="Please sign in with Google first."
        )

    user_id = user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid user session."
        )

    return user

# --------------------------------------------
# Frontend
# --------------------------------------------

@app.get(
    "/",
    include_in_schema=False
)
def root():

    if not INDEX_FILE.exists():

        raise HTTPException(
            status_code=500,
            detail="frontend/index.html was not found."
        )

    return FileResponse(
        str(INDEX_FILE),
        media_type="text/html"
    )


@app.get(
    "/service-worker.js",
    include_in_schema=False
)
def service_worker():

    return FileResponse(
        str(FRONTEND_DIR / "service-worker.js"),
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )

# --------------------------------------------
# NØVA Status
# --------------------------------------------

@app.get("/status")
def status():

    return nova_universal_ai.status()

# --------------------------------------------
# Conversations
# --------------------------------------------

@app.get("/conversations")
def get_conversations(
    request: Request
):

    user = get_current_user(
        request
    )

    conversations = (
        chat_service.list(
            user["user_id"]
        )
    )

    return {
        "success": True,
        "conversations": conversations
    }


@app.post("/conversations")
def create_conversation(
    request: Request,
    data: ConversationCreate
):

    user = get_current_user(
        request
    )

    conversation = (
        chat_service.create(
            user_id=user["user_id"],
            title=data.title
        )
    )

    return {
        "success": True,
        "conversation": conversation
    }


@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    request: Request
):

    user = get_current_user(
        request
    )

    conversation = (
        chat_service.get(
            user_id=user["user_id"],
            conversation_id=conversation_id
        )
    )

    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "success": True,
        "conversation": conversation
    }


@app.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    request: Request
):

    user = get_current_user(
        request
    )

    deleted = (
        chat_service.delete(
            user_id=user["user_id"],
            conversation_id=conversation_id
        )
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "success": True,
        "message": "Conversation deleted."
    }

# --------------------------------------------
# Chat
# --------------------------------------------

@app.post("/chat")
def chat(
    request: Request,
    data: ChatRequest
):

    user = get_current_user(
        request
    )

    result = chat_service.send(
        user_id=user["user_id"],
        conversation_id=data.conversation_id,
        message=data.message
    )

    if not result["success"]:

        return {
            "success": False,
            "response": result["response"],
            "error": result.get("error")
        }

    return {
        "success": True,
        "response": result["response"],
        "conversation": result.get(
            "conversation"
        )
    }

# --------------------------------------------
# Memory
# --------------------------------------------

@app.get("/memory")
def get_memory(request: Request):

    user = get_current_user(request)

    memories = nova_memory.get_memories(
        user["user_id"]
    )

    return {
        "memories": memories,
        "count": len(memories)
    }


@app.post("/memory")
def save_memory(
    request: Request,
    information: str
):

    user = get_current_user(request)

    success = nova_memory.remember(
        information,
        user_id=user["user_id"]
    )

    return {
        "success": success,
        "message": (
            "Memory saved."
            if success
            else "Could not save memory."
        )
    }