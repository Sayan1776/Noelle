import json
from pathlib import Path
from typing import List, Tuple, Optional
from gui.session import ChatSession


SESSION_FILE = Path("data/sessions.json")


def save_sessions(sessions: List[ChatSession], active_id:Optional [str]):
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    data ={
        "active_id": active_id,
        "sessions": [s.to_dict() for s in sessions]
    }

    with open(SESSION_FILE, "w" , encoding= "utf-8") as f:
        json.dump(data, f, indent=2)




def load_sessions() -> tuple[List[ChatSession], Optional[str]]:
    if not SESSION_FILE.exists():
        return [], None

    try:
        with open(SESSION_FILE, "r" , encoding = "utf-8") as f:
            raw = f.read().strip()
            if not raw:
                return [], None

            data = json.loads(raw)
    
    except (json.JSONDecodeError, OSError):
        #corrupted or unreadable file - start fresh
        return [], None
    
    sessions = [ChatSession.from_dict(item)
                for item in data.get("sessions", [])]
    
    active_id = data.get("active_id")
    return sessions, active_id