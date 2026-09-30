"""
NØVA AI — Universal AI Engine

Central brain for:
- General AI Q&A
- Live Google Search grounding
- Local calculations
- Hindi/English/multilingual answers
- Conversation context
- NØVA self-awareness
- Optional OpenAI fallback when Gemini quota is exhausted

Environment variables:
    GEMINI_API_KEY
    NOVA_GEMINI_MODEL       (default: gemini-3.8-flash)
    OPENAI_API_KEY          (optional)
    NOVA_OPENAI_MODEL       (default: gpt-5.6-luna)
    NOVA_PROVIDER           (auto | gemini | openai | nvidia)

This file does not bypass provider quotas. It provides a provider
fallback architecture when another API key is configured.
"""

from __future__ import annotations

import ast
import json
import math
import operator
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from openai import OpenAI

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    PROJECT_ROOT / ".env",
    override=True
)

NOVA_NAME = "NØVA AI"
NOVA_VERSION = "1.0 Universal"

GEMINI_MODEL = os.getenv("NOVA_GEMINI_MODEL", "gemini-3.8-flash")
OPENAI_MODEL = os.getenv("NOVA_OPENAI_MODEL", "gpt-5.6-luna")
PROVIDER = os.getenv("NOVA_PROVIDER", "auto").lower().strip()

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
}

_ALLOWED_NAMES = {"pi": math.pi, "e": math.e}


def _safe_eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in _ALLOWED_NAMES:
        return float(_ALLOWED_NAMES[node.id])
    if isinstance(node, ast.UnaryOp):
        op = _ALLOWED_UNARYOPS.get(type(node.op))
        if op is None:
            raise ValueError("Unsupported unary operator.")
        return float(op(_safe_eval_node(node.operand)))
    if isinstance(node, ast.BinOp):
        op = _ALLOWED_BINOPS.get(type(node.op))
        if op is None:
            raise ValueError("Unsupported binary operator.")
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large.")
        result = op(left, right)
        if not math.isfinite(result):
            raise ValueError("Calculation produced a non-finite result.")
        return float(result)
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function.")
        function = _ALLOWED_FUNCS.get(node.func.id)
        if function is None:
            raise ValueError("Unsupported function.")
        if len(node.args) > 4:
            raise ValueError("Too many function arguments.")
        return float(function(*[_safe_eval_node(arg) for arg in node.args]))
    raise ValueError("Unsupported expression.")


def local_calculate(expression: str) -> Optional[str]:
    expression = expression.strip()
    if not expression or len(expression) > 500:
        return None
    allowed_chars = set("0123456789+-*/%()., abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_^")
    if any(char not in allowed_chars for char in expression):
        return None
    expression = expression.replace("^", "**")
    try:
        tree = ast.parse(expression, mode="eval")
        value = _safe_eval_node(tree.body)
        if value.is_integer():
            return str(int(value))
        return f"{value:.12g}"
    except Exception:
        return None


def needs_web_search(message: str) -> bool:
    text = message.lower().strip()
    current_terms = (
        "latest", "today", "today's", "currently", "current", "right now",
        "recent", "recently", "news", "update", "updates", "price", "prices",
        "weather", "score", "scores", "schedule", "release", "released",
        "launch", "launched", "2026", "this week", "this month", "this year",
    )
    explicit_web_terms = (
        "search the web", "search online", "look it up", "find online",
        "official source", "sources", "references", "website",
    )
    return any(term in text for term in current_terms) or any(term in text for term in explicit_web_terms)


def looks_like_simple_math(message: str) -> bool:
    text = message.lower().strip()
    if any(symbol in text for symbol in ("+", "-", "*", "/", "%", "^")):
        return True
    return any(word in text for word in ("calculate", "calc", "evaluate")) and any(char.isdigit() for char in text)


def extract_math_expression(message: str) -> Optional[str]:
    text = message.strip()
    for prefix in ("calculate ", "calc ", "evaluate "):
        if text.lower().startswith(prefix):
            return text[len(prefix):].strip()
    return text

SYSTEM_INSTRUCTION = """
You are NØVA AI, a powerful general-purpose AI assistant.

Identity:
- Name: NØVA AI
- Version: 1.0 Universal

Behavior:
1. Answer the user's actual question directly.
2. Support Hindi, English, Hinglish, and other languages.
3. For current or changing information, use web grounding when available.
4. Never pretend to know current information if it has not been verified.
5. For mathematics and calculations, prefer exact computation over guessing.
6. Explain difficult answers step-by-step when useful.
7. For coding, provide practical working code.
8. Do not invent facts, sources, events, or actions.
9. If evidence is insufficient, say what is uncertain.
10. When search grounding is enabled, base time-sensitive factual claims on retrieved information.
"""


@dataclass
class NovaResult:
    text: str
    provider: str
    used_web: bool = False
    used_local_calculator: bool = False
    error: Optional[str] = None


class UniversalAI:
    def __init__(self) -> None:
        self.gemini_client: Any = None
        self.gemini_types: Any = None
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.nvidia_key = os.getenv("NVIDIA_API_KEY")
        self.nvidia_base_url = os.getenv(
            "NVIDIA_BASE_URL",
            "https://integrate.api.nvidia.com/v1"
        )
        self.nvidia_model = os.getenv(
            "NVIDIA_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b"
        )

        self.nvidia_client = None

        if self.nvidia_key:
            try:
                self.nvidia_client = OpenAI(
                    base_url=self.nvidia_base_url,
                    api_key=self.nvidia_key
                )

                print(
                    "NØVA: NVIDIA NIM connected."
                )

            except Exception as error:
                print(
                    "NØVA: NVIDIA initialization failed:",
                    error
                )

        self._init_gemini()

    def _init_gemini(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("NØVA: GEMINI_API_KEY is not configured.")
            return
        try:
            from google import genai
            from google.genai import types

            self.gemini_client = genai.Client(api_key=api_key)
            self.gemini_types = types
            print("NØVA: Gemini client initialized.")
        except Exception as error:
            print("NØVA: Gemini initialization failed:", error)
            self.gemini_client = None
            self.gemini_types = None

    def _gemini_available(self) -> bool:
        return self.gemini_client is not None and self.gemini_types is not None

    def _ask_gemini(self, message: str, history: list[dict[str, Any]], use_web: bool) -> NovaResult:
        if not self._gemini_available():
            return NovaResult("", "gemini", use_web=use_web, error="GEMINI_API_KEY or google-genai is unavailable.")

        contents: list[Any] = []
        for item in history[-40:]:
            role = item.get("role")
            text = str(item.get("message", "")).strip()
            if role not in ("user", "model") or not text:
                continue
            contents.append(self.gemini_types.Content(role=role, parts=[self.gemini_types.Part(text=text)]))
        contents.append(self.gemini_types.Content(role="user", parts=[self.gemini_types.Part(text=message)]))

        kwargs: dict[str, Any] = {
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.7,
            "max_output_tokens": 8192,
        }
        if use_web:
            kwargs["tools"] = [self.gemini_types.Tool(google_search=self.gemini_types.GoogleSearch())]

        config = self.gemini_types.GenerateContentConfig(**kwargs)
        try:
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            )
            text = (response.text or "").strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return NovaResult(text, "gemini", used_web=use_web)
        except Exception as exc:
            return NovaResult("", "gemini", used_web=use_web, error=str(exc))

    def _ask_openai(self, message: str, history: list[dict[str, Any]]) -> NovaResult:
        if not self.openai_key:
            return NovaResult("", "openai", error="OPENAI_API_KEY is not configured.")

        input_items: list[dict[str, Any]] = []
        for item in history[-40:]:
            role = item.get("role")
            text = str(item.get("message", "")).strip()
            if role in ("user", "assistant") and text:
                input_items.append({"role": role, "content": text})
        input_items.append({"role": "user", "content": message})

        payload = {
            "model": OPENAI_MODEL,
            "instructions": SYSTEM_INSTRUCTION,
            "input": input_items,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            text = str(data.get("output_text", "")).strip()
            if not text:
                pieces: list[str] = []
                for item in data.get("output", []):
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            pieces.append(str(content.get("text", "")))
                text = "\n".join(pieces).strip()
            if not text:
                raise RuntimeError("OpenAI returned an empty response.")
            return NovaResult(text, "openai")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return NovaResult("", "openai", error=f"HTTP {exc.code}: {body}")
        except Exception as exc:
            return NovaResult("", "openai", error=str(exc))

    def _ask_nvidia(self, message: str, history: list[dict[str, Any]]) -> NovaResult:
        if self.nvidia_client is None or not self.nvidia_model:
            return NovaResult(
                text="",
                provider="nvidia",
                error="NVIDIA NIM is not configured.",
            )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ]
        for item in history[-40:]:
            role = item.get("role")
            if role == "model":
                role = "assistant"
            if role not in {"user", "assistant"}:
                continue
            text = str(item.get("message", "")).strip()
            if text:
                messages.append({"role": role, "content": text})
        messages.append({"role": "user", "content": message})

        try:
            response = (
                self.nvidia_client
                .chat
                .completions
                .create(
                    model=self.nvidia_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096,
                )
            )
            answer = (
                response
                .choices[0]
                .message
                .content
                or ""
            ).strip()
            if not answer:
                raise RuntimeError("NVIDIA returned an empty response.")
            return NovaResult(
                text=answer,
                provider="nvidia",
            )
        except Exception as error:
            return NovaResult(
                text="",
                provider="nvidia",
                error=str(error),
            )

    def ask(self, message: str, history: Optional[list[dict[str, Any]]] = None) -> NovaResult:
        message = message.strip()
        history = history or []
        if not message:
            return NovaResult("Please enter a question.", "local")

        if looks_like_simple_math(message):
            expression = extract_math_expression(message)
            if expression:
                result = local_calculate(expression)
                if result is not None:
                    return NovaResult(f"Answer: {result}", "local-calculator", used_local_calculator=True)

        use_web = needs_web_search(message)
        provider_order = [
            "nvidia",
            "gemini",
            "openai"
        ]
        if PROVIDER in provider_order:
            provider_order.remove(PROVIDER)
            provider_order.insert(0, PROVIDER)

        last_errors: list[str] = []
        for provider in provider_order:
            if provider == "nvidia":
                result = self._ask_nvidia(message, history)
            elif provider == "gemini":
                result = self._ask_gemini(message, history, use_web)
            else:
                result = self._ask_openai(message, history)
            if result.text:
                return result
            if result.error:
                last_errors.append(f"{provider}: {result.error}")

        return NovaResult(
            "NØVA could not get an AI response right now.\n\n" + ("\n".join(last_errors) if last_errors else "No AI provider is configured."),
            "router",
            used_web=use_web,
            error="; ".join(last_errors),
        )

    def status(self) -> dict[str, Any]:
        return {
            "name": NOVA_NAME,
            "version": NOVA_VERSION,
            "gemini_configured": self._gemini_available(),
            "gemini_model": GEMINI_MODEL,
            "openai_configured": bool(self.openai_key),
            "openai_model": OPENAI_MODEL,
            "nvidia_configured": bool(self.nvidia_client and self.nvidia_model),
            "nvidia_model": self.nvidia_model,
            "provider_mode": PROVIDER,
            "capabilities": {
                "general_ai": True,
                "google_search_grounding": self._gemini_available(),
                "local_calculator": True,
                "multilingual": True,
                "conversation_context": True,
                "openai_fallback": bool(self.openai_key),
                "nvidia_fallback": bool(self.nvidia_client and self.nvidia_model),
            },
        }


nova_universal_ai = UniversalAI()


def ask_nova(message: str, history: Optional[list[dict[str, Any]]] = None) -> NovaResult:
    return nova_universal_ai.ask(message, history)
