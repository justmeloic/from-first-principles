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

"""Server-Sent Events (SSE) support for real-time agent status updates."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict

_logger = logging.getLogger(__name__)


class SSEManager:
    """Manages Server-Sent Events for real-time communication with frontend."""

    def __init__(self):
        self._connections: Dict[str, asyncio.Queue] = {}

    def add_connection(self, session_id: str) -> asyncio.Queue:
        """Add a new SSE connection for a session."""
        queue = asyncio.Queue()
        self._connections[session_id] = queue
        _logger.info(f'Added SSE connection for session {session_id}')
        return queue

    def remove_connection(self, session_id: str):
        """Remove an SSE connection."""
        if session_id in self._connections:
            del self._connections[session_id]
            _logger.info(f'Removed SSE connection for session {session_id}')

    async def send_status_update(
        self, session_id: str, status: str, message: str = '', tool_name: str = ''
    ):
        """Send a status update to the frontend."""
        if session_id in self._connections:
            update = {
                'type': 'status_update',
                'status': status,
                'message': message,
                'tool_name': tool_name,
                'timestamp': time.time(),
            }
            try:
                await self._connections[session_id].put(update)
                _logger.debug(f'Sent status update to session {session_id}: {status}')
            except Exception as e:
                _logger.error(
                    f'Error sending status update to session {session_id}: {e}'
                )

    async def send_tool_start(
        self, session_id: str, tool_name: str, estimated_duration: int = None
    ):
        """Send notification that a tool has started."""
        message = f'Processing with {tool_name}...'
        if estimated_duration:
            message += f' (estimated {estimated_duration}s)'

        await self.send_status_update(session_id, 'tool_running', message, tool_name)

    async def send_tool_complete(self, session_id: str, tool_name: str):
        """Send notification that a tool has completed."""
        await self.send_status_update(
            session_id, 'tool_complete', f'{tool_name} completed', tool_name
        )

    async def send_final_response(self, session_id: str, response: str):
        """Send the final response."""
        update = {
            'type': 'final_response',
            'response': response,
            'timestamp': time.time(),
        }
        if session_id in self._connections:
            try:
                await self._connections[session_id].put(update)
            except Exception as e:
                _logger.error(
                    f'Error sending final response to session {session_id}: {e}'
                )

    async def generate_sse_stream(self, session_id: str) -> AsyncGenerator[str, None]:
        """Generate SSE stream for a session."""
        queue = self.add_connection(session_id)

        try:
            while True:
                try:
                    # Wait for updates with a timeout to send keep-alive
                    update = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Format as SSE
                    data = json.dumps(update)
                    yield f'data: {data}\n\n'

                except asyncio.TimeoutError:
                    # Send keep-alive
                    yield 'data: {"type": "keep_alive"}\n\n'

        except Exception as e:
            _logger.error(f'Error in SSE stream for session {session_id}: {e}')
        finally:
            self.remove_connection(session_id)


sse_manager = SSEManager()
