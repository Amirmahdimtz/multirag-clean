from typing import List

from src.domain.models.chat_message import ChatMessage


class ChatHistoryService:
    def build_history_text(self, messages: List[ChatMessage]) -> str:
        history_parts = []

        for msg in messages:
            role = msg.role.value.upper()
            history_parts.append(f"{role}: {msg.content}")

        return "\n".join(history_parts)
