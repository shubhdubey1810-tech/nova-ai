# NØVA AI 1.0
# Memory System

import json
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_FILE = PROJECT_ROOT / "data" / "memory.json"
MEMORY_DIR = PROJECT_ROOT / "data" / "memories"


class NovaMemory:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self._create_memory_file()

    def _create_memory_file(self):
        """Create the memory folder and file if they don't exist."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.memory_file.exists():
            self._save({
                "memories": [],
                "user_preferences": {}
            })

    def _file_for_user(self, user_id):
        safe_id = "".join(
            character
            for character in str(user_id)
            if character.isalnum() or character in "-_"
        )

        if not safe_id:
            raise ValueError("Invalid user ID.")

        return MEMORY_DIR / f"{safe_id}.json"

    def _load_for_user(self, user_id):
        path = self._file_for_user(user_id)

        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "memories": [],
                "user_preferences": {}
            }

    def _save_for_user(self, user_id, data):
        path = self._file_for_user(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _load(self):
        """Load memory from the JSON file."""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "memories": [],
                "user_preferences": {}
            }

    def _save(self, data):
        """Save memory to the JSON file."""
        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def remember(self, information, user_id=None):
        """Save something to NØVA's memory."""
        data = (
            self._load_for_user(user_id)
            if user_id is not None
            else self._load()
        )

        memory = {
            "text": information,
            "created_at": datetime.now().isoformat()
        }

        data["memories"].append(memory)
        if user_id is None:
            self._save(data)
        else:
            self._save_for_user(user_id, data)

        return "I'll remember that."

    def get_memories(self, user_id=None):
        """Return all saved memories."""
        data = (
            self._load_for_user(user_id)
            if user_id is not None
            else self._load()
        )
        return data["memories"]

    def search(self, keyword):
        """Search saved memories."""
        data = self._load()
        keyword = keyword.lower()

        results = []

        for memory in data["memories"]:
            if keyword in memory["text"].lower():
                results.append(memory)

        return results

    def forget_all(self):
        """Delete all stored memories."""
        data = {
            "memories": [],
            "user_preferences": {}
        }

        self._save(data)

        return "All local NØVA memories have been cleared."


# Create the memory system
nova_memory = NovaMemory()


if __name__ == "__main__":
    print("NØVA Memory System 1.0")
    print()

    nova_memory.remember("NØVA AI has been created.")

    print("Saved memories:")
    for memory in nova_memory.get_memories():
        print("-", memory["text"])