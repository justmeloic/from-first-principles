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

"""Agent service for processing queries via the root agent.

This service orchestrates the interaction with the ADK runner,
processes events, and formats the final response.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Dict, Tuple

from fastapi import HTTPException, Request
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types as genai_types
from loguru import logger as _logger

from src.agents.agent_factory import agent_factory
from src.app.models import AgentConfig
from src.app.schemas import AgentResponse, Query
from src.app.utils.formatters import format_text_response
from src.app.utils.sse import sse_manager


class AgentService:
    """Service for handling agent interactions and query processing."""

    def __init__(self):
        """Initialize the agent service."""
        self._logger = _logger

    async def _create_and_log_user_event(
        self,
        session_service: InMemorySessionService,
        session: Session,
        query_text: str,
        model_name: str,
    ) -> genai_types.Content:
        """Creates the user event, appends it to the session, and returns the content.

        Args:
            session_service: The session service instance.
            session: The user session.
            query_text: The user's query text.
            model_name: The model being used for this query.

        Returns:
            The user content for the agent.
        """
        user_content = genai_types.Content(
            role='user', parts=[genai_types.Part(text=query_text)]
        )

        # Get agent name from the factory
        agent = agent_factory.get_agent(model_name)

        user_event = Event(
            author=agent.name,
            content=user_content,
            timestamp=time.time(),
            actions=EventActions(
                state_delta={
                    'last_query': query_text,
                    'last_query_ts': time.time(),
                    'query_count': session.state.get('query_count', 0) + 1,
                    'model_name': model_name,
                }
            ),
            invocation_id=str(uuid.uuid4()),
        )
        await session_service.append_event(session, user_event)
        return user_content

    async def _process_agent_events(
        self,
        request: Request,
        session_service: InMemorySessionService,
        runner: Runner,
        session: Session,
        config: AgentConfig,
        user_content: genai_types.Content,
        model_name: str,
    ) -> Tuple[str, Dict]:
        """Runs the agent and processes the resulting event stream.

        Args:
            request: The FastAPI request object.
            session_service: The session service instance.
            runner: The ADK runner instance.
            session: The user session.
            config: The agent configuration.
            user_content: The user content for the agent.
            model_name: The model being used for this query.

        Returns:
            A tuple of (final_response_text, references_json).
        """
        final_response_text = 'Agent did not produce a final response.'
        references_json = {}
        session_id = session.id

        async for event in runner.run_async(
            user_id=config.user_id,
            session_id=session.id,
            new_message=user_content,
        ):
            await session_service.append_event(session, event)

            # Check if this is a tool call event
            if hasattr(event, 'actions') and event.actions:
                if hasattr(event.actions, 'tool_call') and event.actions.tool_call:
                    tool_name = getattr(event.actions.tool_call, 'name', 'unknown_tool')
                    await sse_manager.send_tool_start(session_id, tool_name)
                    self._logger.info(
                        f'Tool started: {tool_name} for session {session_id}'
                    )

            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text
                final_response_text, references_json = format_text_response(
                    response_text=response_text, request=request
                )

                # Send final response via SSE
                await sse_manager.send_final_response(session_id, final_response_text)

                state_changes = {
                    'last_response': final_response_text,
                    'last_interaction_ts': time.time(),
                    'model_name': model_name,
                }

                # Get agent name from the factory
                agent = agent_factory.get_agent(model_name)

                state_update_event = Event(
                    author=agent.name,
                    actions=EventActions(state_delta=state_changes),
                    timestamp=time.time(),
                    invocation_id=str(uuid.uuid4()),
                )
                await session_service.append_event(session, state_update_event)

        return final_response_text, references_json

    async def process_query(
        self,
        request: Request,
        query: Query,
        config: AgentConfig,
        session: Session,
        runner: Runner,
        model_name: str,
    ) -> AgentResponse:
        """Handles the full lifecycle of an interaction with the agent.

        Args:
            request: The incoming FastAPI request object.
            query: The user's query.
            config: The agent configuration.
            session: The active user session.
            runner: The ADK runner instance.
            model_name: The model being used for this query.

        Raises:
            HTTPException: If an unexpected error occurs during processing.

        Returns:
            An AgentResponse object containing the final response and any references.
        """
        session_id = getattr(request.state, 'actual_session_id', 'UNKNOWN')

        try:
            session_service = request.app.state.session_service
            self._logger.info(
                "Running agent for session '%s' with query: '%s...'",
                session_id,
                query.text[:100],
            )

            user_content = await self._create_and_log_user_event(
                session_service, session, query.text, model_name
            )

            final_response_text, references_json = await self._process_agent_events(
                request,
                session_service,
                runner,
                session,
                config,
                user_content,
                model_name,
            )

            self._logger.info(
                "Successfully processed query for session '%s'. Response: '%s...'",
                session_id,
                final_response_text[:100],
            )

            return AgentResponse(
                response=final_response_text,
                references=references_json,
                session_id=session_id,
                model=model_name,
            )

        except Exception as e:
            self._logger.exception(
                "Error processing agent query for session '%s': %s", session_id, e
            )
            raise HTTPException(
                status_code=500,
                detail={'message': 'Error processing agent query', 'error': str(e)},
            )


agent_service = AgentService()
