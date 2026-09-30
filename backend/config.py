# NØVA AI 1.0
# Configuration

import os
from pathlib import Path


# --------------------------------------------------
# NØVA Information
# --------------------------------------------------

NOVA_NAME = "NØVA AI"
NOVA_VERSION = "1.0.0"
NOVA_DESCRIPTION = "Your Intelligent Personal Assistant"


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
TOOLS_DIR = BASE_DIR / "tools"
CONVERSATIONS_DIR = DATA_DIR / "conversations"

MEMORY_FILE = DATA_DIR / "memory.json"


# Create required directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TOOLS_DIR.mkdir(parents=True, exist_ok=True)
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# AI Settings
# --------------------------------------------------

AI_PROVIDER = os.getenv("NOVA_AI_PROVIDER", "local")

AI_MODEL = os.getenv(
    "NOVA_AI_MODEL",
    "gemini-3.8-flash"
)

AI_TEMPERATURE = 0.7

AI_MAX_TOKENS = 5000


# --------------------------------------------------
# Memory Settings
# --------------------------------------------------

MEMORY_ENABLED = True

MAX_MEMORY_RESULTS = 1000

SAVE_CONVERSATIONS = True


# --------------------------------------------------
# Voice Settings
# --------------------------------------------------

VOICE_ENABLED = True

VOICE_LANGUAGE = os.getenv("NOVA_VOICE_LANGUAGE", "HINDI")
VOICE_GENDER = os.getenv("NOVA_VOICE_GENDER", "MALE")

VOICE_NAME = "NØVA"


# --------------------------------------------------
# Tool Settings
# --------------------------------------------------

TOOLS_ENABLED = True

CODING_TOOLS_ENABLED = True
FILE_TOOLS_ENABLED = True
WEB_TOOLS_ENABLED = True
IMAGE_TOOLS_ENABLED = True
VIDEO_TOOLS_ENABLED = True
AUDIO_TOOLS_ENABLED = True
THREE_D_TOOLS_ENABLED = True


# --------------------------------------------------
# Security Settings
# --------------------------------------------------

REQUIRE_PERMISSION_FOR_FILES = True

REQUIRE_PERMISSION_FOR_SYSTEM_ACTIONS = True

ALLOW_DESTRUCTIVE_ACTIONS = False


# --------------------------------------------------
# Environment / API Keys
# --------------------------------------------------

API_KEY = os.getenv("NOVA_API_KEY", "")


# --------------------------------------------------
# Debug Settings
# --------------------------------------------------

DEBUG = True

LOG_LEVEL = "INFO"


# --------------------------------------------------
# Display Settings
# --------------------------------------------------

SHOW_VERSION = True
SHOW_STARTUP_MESSAGE = True


def get_config():
    """Return the main NØVA configuration."""

    return {
        "name": NOVA_NAME,
        "version": NOVA_VERSION,
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "memory_enabled": MEMORY_ENABLED,
        "tools_enabled": TOOLS_ENABLED,
        "voice_enabled": VOICE_ENABLED,
        "debug": DEBUG,
    }


if __name__ == "__main__":
    print("NØVA Configuration")
    print("=" * 30)

    for key, value in get_config().items():
        print(f"{key}: {value}")