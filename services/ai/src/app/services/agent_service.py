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
Includes semantic caching to reduce latency for repeated similar queries.
"""

from __future__ import annotations

import asyncio
import json
import random
import time
import uuid
from typing import AsyncGenerator, Dict, List, Tuple

from fastapi import HTTPException, Request
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types as genai_types
from loguru import logger as _logger

from src.agents.agent_factory import agent_factory
from src.app.core.config import settings
from src.app.models import AgentConfig
from src.app.schemas import AgentResponse, Query
from src.app.services.semantic_cache import get_semantic_cache
from src.app.utils.formatters import format_text_response
from src.app.utils.sse import sse_manager


class AgentService:
    """Service for handling agent interactions and query processing."""

    def __init__(self):
        """Initialize the agent service."""
        self._logger = _logger

    async def _process_uploaded_files(
        self,
        request: Request,
        session: Session,
        file_artifacts: List[str],
    ) -> str:
        """Process uploaded files and return formatted content for agent context."""
        from src.app.artifacts.file_processors import get_file_processor

        if not file_artifacts:
            return ""

        # Get artifact service from request
        artifact_service = request.app.state.artifact_service

        # Check if artifact service is configured (ADK best practice)
        if artifact_service is None:
            self._logger.error("Artifact service is not configured")
            return (
                "Error: File processing unavailable - artifact service not configured"
            )

        results = []
        for artifact_filename in file_artifacts:
            try:
                # Load artifact using artifact service directly
                artifact = await artifact_service.load_artifact(
                    app_name="agent_app",  # Match the config
                    user_id="default_user",  # Match the config
                    session_id=session.id,
                    filename=artifact_filename,
                )

                # Check return value as recommended in ADK best practices
                if artifact and artifact.inline_data:
                    # Get appropriate processor for the MIME type
                    processor = get_file_processor(artifact.inline_data.mime_type)
                    processed_content = await processor.process(
                        artifact.inline_data.data
                    )
                    results.append(f"File: {artifact_filename}\n{processed_content}")
                else:
                    # Artifact not found or has no content
                    results.append(
                        f"File: {artifact_filename} - Could not load content"
                    )

            except ValueError as e:
                # Handle ADK-specific errors (e.g., service not configured)
                self._logger.error(
                    f"ADK error processing file {artifact_filename}: {e}"
                )
                results.append(f"File: {artifact_filename} - Service error: {e}")
            except Exception as e:
                # Handle other unexpected errors
                self._logger.error(
                    f"Unexpected error processing file {artifact_filename}: {e}"
                )
                results.append(f"File: {artifact_filename} - Error processing: {e}")

        return "\n\n".join(results)

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
            role="user", parts=[genai_types.Part(text=query_text)]
        )

        # Get agent name from the factory
        agent = agent_factory.get_agent(model_name)

        user_event = Event(
            author=agent.name,
            content=user_content,
            timestamp=time.time(),
            actions=EventActions(
                state_delta={
                    "last_query": query_text,
                    "last_query_ts": time.time(),
                    "query_count": session.state.get("query_count", 0) + 1,
                    "model_name": model_name,
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
        final_response_text = "Agent did not produce a final response."
        references_json = {}
        session_id = session.id

        # Retry loop with exponential backoff and jitter
        for attempt in range(settings.RETRY_MAX_ATTEMPTS):
            try:
                async for event in runner.run_async(
                    user_id=config.user_id,
                    session_id=session.id,
                    new_message=user_content,
                ):
                    await session_service.append_event(session, event)

                    # Check if this is a tool call event
                    if hasattr(event, "actions") and event.actions:
                        if (
                            hasattr(event.actions, "tool_call")
                            and event.actions.tool_call
                        ):
                            tool_name = getattr(
                                event.actions.tool_call, "name", "unknown_tool"
                            )
                            await sse_manager.send_tool_start(session_id, tool_name)
                            self._logger.info(
                                f"Tool started: {tool_name} for session {session_id}"
                            )

                    if (
                        event.is_final_response()
                        and event.content
                        and event.content.parts
                    ):
                        response_text = event.content.parts[0].text
                        final_response_text, references_json = format_text_response(
                            response_text=response_text, request=request
                        )

                        # Send final response via SSE
                        await sse_manager.send_final_response(
                            session_id, final_response_text
                        )

                        state_changes = {
                            "last_response": final_response_text,
                            "last_interaction_ts": time.time(),
                            "model_name": model_name,
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

                # Success - break out of retry loop
                break

            except Exception as e:
                if attempt < settings.RETRY_MAX_ATTEMPTS - 1:
                    # Exponential backoff with jitter
                    delay = settings.RETRY_BASE_DELAY * (2**attempt)
                    jitter = delay * random.uniform(0.5, 1.5)
                    max_attempts = settings.RETRY_MAX_ATTEMPTS
                    self._logger.warning(
                        f"Agent call failed (attempt {attempt + 1}/{max_attempts})"
                        f": {e}. Retrying in {jitter:.2f}s..."
                    )
                    await asyncio.sleep(jitter)
                else:
                    max_attempts = settings.RETRY_MAX_ATTEMPTS
                    self._logger.error(
                        f"Agent call failed after {max_attempts} attempts: {e}"
                    )
                    raise

        return final_response_text, references_json

    async def _check_semantic_cache(
        self,
        query_text: str,
        model_name: str,
    ) -> Tuple[bool, str, Dict]:
        """Check if a semantically similar query exists in the cache.

        Args:
            query_text: The user's query text.
            model_name: The model being used.

        Returns:
            Tuple of (is_cache_hit, cached_response, empty_references).
        """
        try:
            cache = get_semantic_cache()
            cache_entry = await cache.get(query_text, model_name)

            if cache_entry:
                score = cache_entry.similarity_score
                self._logger.info(
                    f"Semantic cache hit (similarity: {score:.4f}) "
                    f'for query: "{query_text[:50]}..."'
                )
                return True, cache_entry.response, {}

            return False, "", {}

        except Exception as e:
            self._logger.warning(f"Error checking semantic cache: {e}")
            return False, "", {}

    async def _store_in_semantic_cache(
        self,
        query_text: str,
        response_text: str,
        model_name: str,
    ) -> None:
        """Store a query-response pair in the semantic cache.

        Args:
            query_text: The user's query text.
            response_text: The LLM's response.
            model_name: The model that generated the response.
        """
        try:
            cache = get_semantic_cache()
            await cache.put(query_text, response_text, model_name)
            self._logger.debug(
                f'Stored response in semantic cache for query: "{query_text[:50]}..."'
            )
        except Exception as e:
            self._logger.warning(f"Error storing in semantic cache: {e}")

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

        Includes semantic caching to reduce latency for repeated similar queries.
        The cache stores query-response pairs and retrieves cached responses
        for semantically similar queries, bypassing the LLM when possible.

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
        session_id = getattr(request.state, "actual_session_id", "UNKNOWN")

        try:
            session_service = request.app.state.session_service
            self._logger.info(
                "Running agent for session '%s' with query: '%s...'",
                session_id,
                query.text[:100],
            )

            # Process uploaded files if present
            file_context = ""
            if query.file_artifacts:
                file_context = await self._process_uploaded_files(
                    request, session, query.file_artifacts
                )

                # Enhance the user's message with file content
                enhanced_query_text = (
                    f"{query.text}\n\n"
                    f"[Files uploaded with this message:]\n{file_context}"
                )
            else:
                enhanced_query_text = query.text

            # Check semantic cache for similar queries (skip for file uploads)
            # File uploads have unique contexts and shouldn't be cached
            if not query.file_artifacts:
                (
                    is_cache_hit,
                    cached_response,
                    cached_refs,
                ) = await self._check_semantic_cache(query.text, model_name)

                if is_cache_hit:
                    self._logger.info(
                        "Returning cached response for session '%s'",
                        session_id,
                    )
                    return AgentResponse(
                        response=cached_response,
                        references=cached_refs,
                        session_id=session_id,
                        model=model_name,
                        cached=True,  # Indicate this was a cache hit
                    )

            user_content = await self._create_and_log_user_event(
                session_service, session, enhanced_query_text, model_name
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

            # Store response in semantic cache (only for queries without file uploads)
            if not query.file_artifacts:
                await self._store_in_semantic_cache(
                    query.text, final_response_text, model_name
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
                cached=False,  # Fresh response from LLM
            )

        except Exception as e:
            self._logger.exception(
                "Error processing agent query for session '%s': %s", session_id, e
            )
            raise HTTPException(
                status_code=500,
                detail={"message": "Error processing agent query", "error": str(e)},
            )

    async def stream_query(
        self,
        request: Request,
        query: Query,
        config: AgentConfig,
        session: Session,
        runner: Runner,
        model_name: str,
    ) -> AsyncGenerator[str, None]:
        """Stream agent response as SSE events with token-level streaming.

        This method yields SSE-formatted events as the agent generates its
        response, enabling real-time word-by-word display in the frontend.

        Args:
            request: The incoming FastAPI request object.
            query: The user's query.
            config: The agent configuration.
            session: The active user session.
            runner: The ADK runner instance.
            model_name: The model being used for this query.

        Yields:
            SSE-formatted strings containing token, tool, or status events.
        """
        session_id = session.id

        def _format_sse(event_type: str, data: dict) -> str:
            """Format data as an SSE event."""
            payload = {"type": event_type, **data, "timestamp": time.time()}
            return f"data: {json.dumps(payload)}\n\n"

        try:
            session_service = request.app.state.session_service
            self._logger.info(
                "Starting streaming for session '%s' with query: '%s...'",
                session_id,
                query.text[:100],
            )

            # Process uploaded files if present
            file_context = ""
            if query.file_artifacts:
                file_context = await self._process_uploaded_files(
                    request, session, query.file_artifacts
                )
                enhanced_query_text = (
                    f"{query.text}\n\n"
                    f"[Files uploaded with this message:]\n{file_context}"
                )
            else:
                enhanced_query_text = query.text

            # Create user event
            user_content = await self._create_and_log_user_event(
                session_service, session, enhanced_query_text, model_name
            )

            # Yield initial status
            yield _format_sse("status", {"message": "Processing query..."})

            # Accumulate the full response for final formatting
            accumulated_text = ""
            final_response_text = ""
            references_json = {}

            # Run agent with streaming enabled (SSE mode for token-level streaming)
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)
            async for event in runner.run_async(
                user_id=config.user_id,
                session_id=session.id,
                new_message=user_content,
                run_config=run_config,
            ):
                await session_service.append_event(session, event)

                # Check for tool calls
                if hasattr(event, "actions") and event.actions:
                    if hasattr(event.actions, "tool_call") and event.actions.tool_call:
                        tool_name = getattr(
                            event.actions.tool_call, "name", "unknown_tool"
                        )
                        yield _format_sse(
                            "tool_start",
                            {
                                "tool_name": tool_name,
                                "message": f"Using {tool_name}...",
                            },
                        )
                        self._logger.debug(
                            f"Tool started: {tool_name} for session {session_id}"
                        )

                # Stream content tokens
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            # Check if this is an incremental token or full response
                            if event.is_final_response():
                                # Final response - format and yield completion
                                (
                                    final_response_text,
                                    references_json,
                                ) = format_text_response(
                                    response_text=part.text, request=request
                                )
                            else:
                                # Streaming token - yield it
                                yield _format_sse("token", {"content": part.text})
                                accumulated_text += part.text

            # If we got content from streaming, use that; otherwise use final_response
            if not final_response_text and accumulated_text:
                final_response_text, references_json = format_text_response(
                    response_text=accumulated_text, request=request
                )

            # Update session state
            if final_response_text:
                agent = agent_factory.get_agent(model_name)
                state_update_event = Event(
                    author=agent.name,
                    actions=EventActions(
                        state_delta={
                            "last_response": final_response_text,
                            "last_interaction_ts": time.time(),
                            "model_name": model_name,
                        }
                    ),
                    timestamp=time.time(),
                    invocation_id=str(uuid.uuid4()),
                )
                await session_service.append_event(session, state_update_event)

            # Yield completion event with full response
            yield _format_sse(
                "complete",
                {
                    "response": final_response_text
                    or "Agent did not produce a response.",
                    "references": references_json,
                    "model": model_name,
                    "session_id": session_id,
                },
            )

            self._logger.info(
                "Completed streaming for session '%s'. Response length: %d",
                session_id,
                len(final_response_text),
            )

        except Exception as e:
            self._logger.exception(
                "Error streaming agent query for session '%s': %s", session_id, e
            )
            yield _format_sse("error", {"message": str(e)})


agent_service = AgentService()
