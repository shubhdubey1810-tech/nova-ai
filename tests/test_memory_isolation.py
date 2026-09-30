import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.memory import NovaMemory


class NovaMemoryIsolationTests(unittest.TestCase):
    def test_memories_are_separate_per_user(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            with (
                patch("backend.memory.MEMORY_DIR", root / "users"),
                patch("backend.memory.MEMORY_FILE", root / "legacy.json"),
            ):
                memory = NovaMemory()
                memory.remember("private to A", user_id="account-A")
                memory.remember("private to B", user_id="account-B")

                self.assertEqual(
                    [item["text"] for item in memory.get_memories("account-A")],
                    ["private to A"]
                )
                self.assertEqual(
                    [item["text"] for item in memory.get_memories("account-B")],
                    ["private to B"]
                )

    def test_user_id_cannot_escape_memory_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            with patch("backend.memory.MEMORY_DIR", root):
                memory = NovaMemory()

                self.assertEqual(
                    memory._file_for_user("../../account").parent,
                    root
                )


if __name__ == "__main__":
    unittest.main()