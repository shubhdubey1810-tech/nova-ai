"""
Compatibility layer for NØVA AI.
The actual AI brain lives in universal_ai_engine.py
"""

from .universal_ai_engine import (
    nova_universal_ai,
    ask_nova,
)

# Keep the old name so existing code does not break.
nova_engine = nova_universal_ai