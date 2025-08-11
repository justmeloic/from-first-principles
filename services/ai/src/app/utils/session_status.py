# Copyright 2025 Loïc Muhirwa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Session status tracking for agent operations."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class AgentStatus(str, Enum):
    """Possible agent status values."""

    IDLE = 'idle'
    PROCESSING = 'processing'
    TOOL_RUNNING = 'tool_running'
    GENERATING_RESPONSE = 'generating_response'
    COMPLETE = 'complete'
    ERROR = 'error'


@dataclass
class SessionStatus:
    """Represents the current status of an agent session."""

    status: AgentStatus
    message: str = ''
    tool_name: str = ''
    estimated_completion: Optional[float] = None  # Unix timestamp
    last_updated: float = 0.0

    def __post_init__(self):
        if self.last_updated == 0.0:
            self.last_updated = time.time()


class SessionStatusTracker:
    """Tracks the status of agent sessions."""

    def __init__(self):
        self._session_statuses: Dict[str, SessionStatus] = {}

    def update_status(
        self,
        session_id: str,
        status: AgentStatus,
        message: str = '',
        tool_name: str = '',
        estimated_duration: Optional[int] = None,
    ):
        """Update the status for a session."""
        estimated_completion = None
        if estimated_duration:
            estimated_completion = time.time() + estimated_duration

        self._session_statuses[session_id] = SessionStatus(
            status=status,
            message=message,
            tool_name=tool_name,
            estimated_completion=estimated_completion,
            last_updated=time.time(),
        )

    def get_status(self, session_id: str) -> Optional[SessionStatus]:
        """Get the current status for a session."""
        return self._session_statuses.get(session_id)

    def clear_status(self, session_id: str):
        """Clear the status for a session."""
        self._session_statuses.pop(session_id, None)

    def cleanup_old_sessions(self, max_age_seconds: int = 3600):
        """Remove sessions older than max_age_seconds."""
        current_time = time.time()
        expired_sessions = [
            session_id
            for session_id, status in self._session_statuses.items()
            if current_time - status.last_updated > max_age_seconds
        ]
        for session_id in expired_sessions:
            del self._session_statuses[session_id]


session_tracker = SessionStatusTracker()
