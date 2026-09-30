"""
NØVA AI
Google Search Grounding Tool
"""

try:
    from google.genai import types
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    types = None


class GoogleSearchTool:
    """
    Enables Gemini to use Google Search grounding.

    Gemini decides when search is useful and returns
    grounded answers with source annotations.
    """

    def __init__(self):
        if types is None:
            raise ModuleNotFoundError(
                "google-genai is not installed. Please install requirements.txt."
            )
        self.tool = types.Tool(
            google_search=types.GoogleSearch()
        )

    def config(self):
        if types is None:
            raise ModuleNotFoundError(
                "google-genai is not installed. Please install requirements.txt."
            )
        return types.GenerateContentConfig(
            tools=[self.tool],
            max_output_tokens=4096,
        )


google_search_tool = GoogleSearchTool() if types is not None else None