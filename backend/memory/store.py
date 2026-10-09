from typing import Dict, List


conversation_memory: Dict[str, List[dict]] = {}


def get_history(session_id: str):
    return conversation_memory.get(session_id, [])


def add_message(
    session_id: str,
    role: str,
    content: str
):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append({
        "role": role,
        "content": content
    })


def get_recent_history(
    session_id: str,
    limit: int = 6
):
    history = get_history(session_id)

    return history[-limit:]


def clear_history(session_id: str):
    conversation_memory.pop(session_id, None)