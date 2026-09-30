"""
NØVA AI
Smart Query Router
"""

import re


class NovaRouter:
    """
    Decides whether a question should use live web grounding.
    """

    CURRENT_KEYWORDS = {
        "latest",
        "today",
        "todays",
        "currently",
        "current",
        "now",
        "recent",
        "recently",
        "news",
        "update",
        "updates",
        "new",
        "price",
        "prices",
        "weather",
        "score",
        "scores",
        "schedule",
        "release",
        "released",
        "launch",
        "launched",
        "2026",
        "this week",
        "this month",
        "this year",
    }

    WEB_PATTERNS = [
        r"\bwho is\b",
        r"\bwhat happened\b",
        r"\bwhere is\b",
        r"\bwhen is\b",
        r"\bhow much\b",
        r"\bsearch\b",
        r"\bfind\b",
        r"\bonline\b",
        r"\bwebsite\b",
        r"\bofficial\b",
        r"\bsource\b",
        r"\breference\b",
    ]

    def needs_web_search(
        self,
        message: str
    ) -> bool:

        text = (
            message
            .strip()
            .lower()
        )

        if not text:
            return False

        # Current/recent information.
        for keyword in self.CURRENT_KEYWORDS:

            if keyword in text:
                return True

        # Explicit web/research-style requests.
        for pattern in self.WEB_PATTERNS:

            if re.search(
                pattern,
                text
            ):
                return True

        return False


nova_router = NovaRouter()