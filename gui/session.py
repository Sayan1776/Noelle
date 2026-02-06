from typing import List, Optional, Dict, Any
from agent.loop import AgentResult


class ChatSession:
    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title
        self.chat_memory: List[Dict[str, str]] = []
        self.last_agent_result: Optional[AgentResult] = None

    # ----------------------------
    # Persistence
    # ----------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "chat_memory": self.chat_memory,
            "last_agent_result": self.last_agent_result,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        session = cls(
            id=data["id"],
            title=data.get("title", "Untitled Chat"),
        )
        session.chat_memory = data.get("chat_memory", [])
        session.last_agent_result = data.get("last_agent_result")
        return session