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

"""Middleware for managing user session IDs and authentication via HTTP headers.

This module provides a Starlette/FastAPI middleware that intercepts requests
to API paths, retrieves or generates a session ID, handles authentication,
and makes session data available to downstream application logic via the
request state. It also ensures the session ID is returned in the response headers.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta

from loguru import logger as _logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.status import HTTP_401_UNAUTHORIZED

from src.app.models import AgentConfig
from src.app.utils.dependencies import get_or_create_session


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to manage a session ID and authentication for requests.

    This middleware performs the following steps:
    1. For paths under `/api/v1/`: Manages session IDs and authentication state
    2. For static frontend paths: Checks authentication for protected routes
    3. Looks for existing session ID in the `X-Session-ID` request header
    4. If no ID is found, generates a new UUIDv4
    5. Stores session data in `request.state` for downstream use
    6. Ensures session ID is present in response headers
    """

    def __init__(self, app):
        super().__init__(app)
        # Paths that don't require authentication
        self.public_paths = {
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json',
            '/api/v1/auth/login',
            '/api/v1/auth/logout',
            '/login',
            '/login.html',
            '/_next',  # Next.js static assets
        }

    def _is_public_path(self, path: str) -> bool:
        """Check if a path is public and doesn't require authentication."""
        # Check for common static file extensions
        if any(
            path.endswith(ext)
            for ext in [
                '.css',
                '.js',
                '.svg',
                '.png',
                '.jpg',
                '.jpeg',
                '.gif',
                '.ico',
                '.woff',
                '.woff2',
                '.txt',
                '.json',
            ]
        ):
            return True

        # Check exact matches
        if path in self.public_paths:
            return True

        # Check path prefixes for static assets
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True

        return False

    async def _is_authenticated(self, request: Request) -> bool:
        """Check if the current session is authenticated."""
        try:
            # Create a dummy response object to satisfy the dependency
            dummy_response = Response(status_code=200)

            # Create the agent config dependency
            agent_config = AgentConfig(app_name='agent_app', user_id='default_user')

            session = await get_or_create_session(request, dummy_response, agent_config)

            # Check if authenticated flag is set in session state
            return session.state.get('authenticated', False)

        except Exception as e:
            session_id = getattr(request.state, 'candidate_session_id', 'N/A')
            _logger.warning(
                f'Error checking authentication for session {session_id}: {e}'
            )
            return False

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Handles the middleware logic for a single request.

        Args:
            request: The incoming Starlette request.
            call_next: A function to call the next middleware or endpoint.

        Returns:
            The Starlette response.
        """
        # Handle session ID for all requests
        candidate_session_id = request.headers.get('X-Session-ID')

        if not candidate_session_id:
            candidate_session_id = str(uuid.uuid4())
            _logger.info(
                'Generated new session ID: %s for path: %s',
                candidate_session_id,
                request.url.path,
            )
        else:
            _logger.info(
                'Using existing session ID: %s for path: %s',
                candidate_session_id,
                request.url.path,
            )

        # Store the session ID on the request state for access in dependencies
        request.state.candidate_session_id = candidate_session_id

        response = await call_next(request)

        # Ensure the final session ID from the request lifecycle is in the header
        actual_session_id = getattr(
            request.state, 'actual_session_id', candidate_session_id
        )
        response.headers['X-Session-ID'] = actual_session_id

        # NOTE: To allow a browser's JavaScript to read the `X-Session-ID`
        # header, it must be listed in `Access-Control-Expose-Headers`.
        # TODO: This logic can also be configured globally in the main
        #       FastAPI CORS middleware setup for better centralization.
        current_exposed = response.headers.get('Access-Control-Expose-Headers')
        if current_exposed:
            exposed_set = {h.strip() for h in current_exposed.split(',')}
            if 'X-Session-ID' not in exposed_set:
                exposed_set.add('X-Session-ID')
                response.headers['Access-Control-Expose-Headers'] = ', '.join(
                    sorted(list(exposed_set))
                )
        else:
            response.headers['Access-Control-Expose-Headers'] = 'X-Session-ID'

        _logger.info(
            'Set session ID in response headers: %s for path: %s',
            actual_session_id,
            request.url.path,
        )
        return response
