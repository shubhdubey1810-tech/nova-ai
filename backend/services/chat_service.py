"""
NØVA AI
Chat + Multi Conversation Service
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..universal_ai_engine import nova_universal_ai
from ..universal_solver import universal_solver


PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)

CONVERSATIONS_DIR = (
    PROJECT_ROOT
    / "data"
    / "conversations"
)

CONVERSATIONS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


class ChatService:

    def _safe_user_id(
        self,
        user_id: str
    ) -> str:

        return "".join(
            character

            for character
            in str(user_id)

            if (
                character.isalnum()
                or character in "-_"
            )
        )


    def _file(
        self,
        user_id: str
    ) -> Path:

        safe_id = (
            self._safe_user_id(
                user_id
            )
        )

        if not safe_id:

            raise ValueError(
                "Invalid user ID."
            )

        return (
            CONVERSATIONS_DIR
            / f"{safe_id}.json"
        )


    def _now(self) -> str:

        return (
            datetime.now(
                timezone.utc
            ).isoformat()
        )


    def _load(
        self,
        user_id: str
    ) -> dict[str, Any]:

        file_path = self._file(
            user_id
        )


        if not file_path.exists():

            return {
                "conversations": []
            }


        try:

            with file_path.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )


            if (
                isinstance(data, dict)
                and isinstance(
                    data.get(
                        "conversations"
                    ),
                    list
                )
            ):

                return data


        except Exception:

            pass


        return {
            "conversations": []
        }


    def _save(
        self,
        user_id: str,
        data: dict[str, Any]
    ) -> None:

        file_path = self._file(
            user_id
        )

        with file_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )


    def _find(
        self,
        data: dict[str, Any],
        conversation_id: str
    ):

        for conversation in (
            data["conversations"]
        ):

            if (
                conversation["id"]
                == conversation_id
            ):

                return conversation

        return None


    # =========================================
    # CREATE
    # =========================================

    def create(
        self,
        user_id: str,
        title: str = "New Chat"
    ):

        data = self._load(
            user_id
        )

        now = self._now()

        conversation = {

            "id":
                uuid.uuid4().hex,

            "title":
                title.strip()
                or "New Chat",

            "created_at":
                now,

            "updated_at":
                now,

            "messages":
                []
        }


        data[
            "conversations"
        ].insert(
            0,
            conversation
        )


        self._save(
            user_id,
            data
        )


        return conversation


    # =========================================
    # LIST
    # =========================================

    def list(
        self,
        user_id: str
    ):

        data = self._load(
            user_id
        )

        conversations = (
            data["conversations"]
        )


        conversations.sort(
            key=lambda item:
                item.get(
                    "updated_at",
                    ""
                ),
            reverse=True
        )


        return [

            {
                "id":
                    item["id"],

                "title":
                    item.get(
                        "title",
                        "New Chat"
                    ),

                "created_at":
                    item.get(
                        "created_at"
                    ),

                "updated_at":
                    item.get(
                        "updated_at"
                    ),

                "message_count":
                    len(
                        item.get(
                            "messages",
                            []
                        )
                    ),
            }

            for item
            in conversations
        ]


    # =========================================
    # GET
    # =========================================

    def get(
        self,
        user_id: str,
        conversation_id: str
    ):

        data = self._load(
            user_id
        )

        return self._find(
            data,
            conversation_id
        )


    # =========================================
    # DELETE
    # =========================================

    def delete(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:

        data = self._load(
            user_id
        )

        old_count = len(
            data["conversations"]
        )


        data["conversations"] = [

            item

            for item
            in data["conversations"]

            if item["id"]
            != conversation_id
        ]


        if len(
            data["conversations"]
        ) == old_count:

            return False


        self._save(
            user_id,
            data
        )

        return True


    # =========================================
    # SEND MESSAGE
    # =========================================

    def send(
        self,
        user_id: str,
        conversation_id: str,
        message: str
    ):

        message = (
            message.strip()
        )


        if not message:

            return {
                "success":
                    False,

                "response":
                    "Please enter a message."
            }


        data = self._load(
            user_id
        )


        conversation = self._find(
            data,
            conversation_id
        )


        if conversation is None:

            return {
                "success":
                    False,

                "response":
                    "Conversation not found."
            }


        # -------------------------------------
        # First message = chat title
        # -------------------------------------

        if not conversation["messages"]:

            title = " ".join(
                message.split()
            )

            if len(title) > 50:

                title = (
                    title[:50]
                    + "..."
                )

            conversation["title"] = (
                title
                or "New Chat"
            )


        # -------------------------------------
        # Add user message
        # -------------------------------------

        conversation[
            "messages"
        ].append({

            "role":
                "user",

            "message":
                message,

            "time":
                self._now()
        })


        local_answer = universal_solver.solve(
            message
        )

        if local_answer is not None:

            conversation[
                "messages"
            ].append({

                "role": "model",

                "message": local_answer,

                "time": self._now()
            })

            conversation[
                "updated_at"
            ] = self._now()

            self._save(
                user_id,
                data
            )

            return {
                "success": True,
                "response": local_answer,
                "used_local_solver": True,
                "used_web": False,
                "conversation": {
                    "id": conversation["id"],
                    "title": conversation["title"],
                    "updated_at": conversation["updated_at"],
                }
            }


        # -------------------------------------
        history = (
            conversation[
                "messages"
            ][:-1]
        )


        # -------------------------------------
        # Ask NØVA
        # -------------------------------------

        result = nova_universal_ai.ask(
            message=message,
            history=history
        )

        if result.error:
            return {
                "success":
                    False,

                "response":
                    result.text
            }

        answer = result.text


        # -------------------------------------
        # Save AI response
        # -------------------------------------

        conversation[
            "messages"
        ].append({

            "role":
                "model",

            "message":
                answer,

            "time":
                self._now()
        })


        conversation[
            "updated_at"
        ] = self._now()


        self._save(
            user_id,
            data
        )


        return {

            "success":
                True,

            "response":
                answer,

            "used_web":
                result.used_web,

            "conversation":
                {

                    "id":
                        conversation["id"],

                    "title":
                        conversation["title"],

                    "updated_at":
                        conversation[
                            "updated_at"
                        ],
                }
        }


chat_service = ChatService()