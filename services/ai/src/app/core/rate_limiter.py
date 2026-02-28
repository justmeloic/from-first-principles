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

"""Rate limiting configuration for API endpoints.

Uses slowapi to provide per-session and global rate limiting on expensive
endpoints (e.g., agent queries that call LLM APIs). The limiter keys on the
X-Session-ID header, falling back to client IP when the header is absent."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from src.app.core.config import settings


def _get_session_or_ip(request: Request) -> str:
    """Extract rate-limit key from X-Session-ID header, falling back to IP."""
    session_id = request.headers.get('X-Session-ID')
    if session_id:
        return session_id
    return get_remote_address(request)


def _global_key(request: Request) -> str:
    """Return a fixed key so all requests share one global bucket."""
    return 'global'


limiter = Limiter(key_func=_get_session_or_ip)

AGENT_RATE_LIMIT: str = settings.AGENT_RATE_LIMIT
GLOBAL_AGENT_RATE_LIMIT: str = settings.GLOBAL_AGENT_RATE_LIMIT
