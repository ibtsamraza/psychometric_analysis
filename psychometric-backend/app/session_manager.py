import time
from typing import Dict, Any

# In-memory store for session statuses
session_status: Dict[str, Dict[str, Any]] = {}

async def update_session_status(
    session_id: str,
    agent: str,
    status: str,
    progress: int,
    name: str = ""
) -> None:
    """
    Update progress and status for a given session.

    Args:
        session_id: Unique identifier for the session
        agent: Name of the current analysis step or agent
        status: Human-readable status message
        progress: Progress percentage (0-100)
        name: Name of the analysis (e.g., sheet name)
    """
    # Create or update the session status record
    session_status.setdefault(session_id, {})
    session_status[session_id].update({
        "agent": agent,
        "status": status,
        "progress": progress,
        "timestamp": time.time(),
        "name": name
    })
    # Optionally, emit via Socket.IO or SSE here


