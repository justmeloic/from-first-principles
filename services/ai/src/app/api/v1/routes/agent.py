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

"""Root Agent Router Module.

This module handles the routing and execution of the root agent's conversation
endpoints. It manages session state purely through ADK's SessionService and
handles agent interactions through FastAPI endpoints.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
from loguru import logger as _logger

from src.agents.agent_factory import agent_factory
from src.app.models import AgentConfig
from src.app.schemas import AgentResponse, Query
from src.app.services.agent_service import agent_service
from src.app.utils.dependencies import (
    get_agent_config,
    get_or_create_session,
    get_runner,
    get_session_model,
)
from src.app.utils.sse import sse_manager

router = APIRouter()


@router.get('/models')
async def get_available_models():
    """Get list of available models.

    Returns:
        Dictionary of available models with their configurations.
    """
    return {
        'models': agent_factory.get_available_models(),
        'default_model': agent_factory.get_default_model(),
    }


@router.post('/', response_model=AgentResponse)
async def agent_endpoint(
    request: Request,
    response: Response,
    query: Query,
    config: Annotated[AgentConfig, Depends(get_agent_config)],
) -> AgentResponse:
    """Processes a user query via the appropriate agent model.

    Args:
        request: The incoming FastAPI request object.
        response: The outgoing FastAPI response object.
        query: The validated request body containing the user's query text
            and optional model.
        config: The agent configuration, injected as a dependency.

    Returns:
        An AgentResponse object containing the agent's response and metadata.
    """
    # Set the selected model in request state for dependencies to use
    request.state.selected_model = query.model

    # Get dependencies with model-specific configurations
    session = await get_or_create_session(request, response, config)
    model_name = await get_session_model(request)
    runner = get_runner(request, config, model_name)

    _logger.info('Received query for model %s: %s...', model_name, query.text[:50])

    return await agent_service.process_query(
        request=request,
        query=query,
        config=config,
        session=session,
        runner=runner,
        model_name=model_name,
    )


@router.get('/events/{session_id}')
async def sse_endpoint(session_id: str) -> StreamingResponse:
    """Server-Sent Events endpoint for real-time status updates.

    Args:
        session_id: The session ID to stream events for.

    Returns:
        A StreamingResponse that sends real-time updates to the frontend.
    """
    _logger.info('Starting SSE stream for session: %s', session_id)

    return StreamingResponse(
        sse_manager.generate_sse_stream(session_id),
        media_type='text/plain',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
        },
    )
