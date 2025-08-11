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

"""Dependency injection module for the root agent router."""

from __future__ import annotations

import logging
import time
import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session

from src.agents.agent_factory import agent_factory
from src.app.core.config import settings
from src.app.models import AgentConfig

_logger = logging.getLogger(__name__)


@lru_cache
def get_agent_config() -> AgentConfig:
    """Gets and caches the agent configuration from application settings.

    Returns:
        The agent configuration object.
    """
    return AgentConfig(
        app_name='agent_app',  # You can add this to settings if needed
        user_id='default_user',  # You can add this to settings if needed
    )


def get_session_service(request: Request) -> InMemorySessionService:
    """Gets the session service instance from the application state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        An instance of InMemorySessionService.
    """
    return request.app.state.session_service


async def get_session_model(
    request: Request,
) -> str:
    """Determine which model to use for this request.

    Priority order:
    1. Model specified in request body (parsed separately)
    2. Session default model
    3. System default model

    Args:
        request: The FastAPI request object

    Returns:
        The model name to use for this request
    """
    # We'll get the model from the request state, set by the endpoint
    model_name = getattr(request.state, 'selected_model', None)

    if not model_name or model_name not in settings.AVAILABLE_MODELS:
        model_name = settings.DEFAULT_MODEL

    _logger.info(f'Selected model: {model_name}')
    return model_name


async def get_or_create_session(
    request: Request,
    response: Response,
    config: Annotated[AgentConfig, Depends(get_agent_config)],
) -> Session:
    """Gets an existing session or creates a new one.

    It retrieves the session ID from the request state (set by middleware),
    and ensures the final session ID is set in the response headers.

    Args:
        request: The incoming FastAPI request object.
        response: The outgoing FastAPI response object.
        config: The agent configuration.

    Returns:
        An active ADK session object.
    """
    session_service = get_session_service(request)
    candidate_session_id = request.state.candidate_session_id
    _logger.info('Processing request with session ID: %s', candidate_session_id)

    session = None
    if candidate_session_id:
        # get_session returns None if not found; it does not raise an exception.
        session = await session_service.get_session(
            app_name=config.app_name,
            user_id=config.user_id,
            session_id=candidate_session_id,
        )

    if session:
        _logger.info('Found existing session: %s', session.id)
    else:
        if candidate_session_id:
            _logger.info('Session not found, creating new: %s', candidate_session_id)
        session_id = candidate_session_id or str(uuid.uuid4())
        _logger.info('Creating new session with ID: %s', session_id)
        initial_state = {
            'app_name': config.app_name,
            'user_id': config.user_id,
            'created_at': time.time(),
            'query_count': 0,
            'default_model': settings.DEFAULT_MODEL,
            'last_used_model': None,
        }
        session = await session_service.create_session(
            app_name=config.app_name,
            user_id=config.user_id,
            session_id=session_id,
            state=initial_state,
        )

    request.state.actual_session_id = session.id
    response.headers['X-Session-ID'] = session.id
    response.headers['Access-Control-Expose-Headers'] = 'X-Session-ID'
    _logger.info('Using session ID: %s', session.id)

    return session


def get_runner(
    request: Request,
    config: Annotated[AgentConfig, Depends(get_agent_config)],
    model_name: Annotated[str, Depends(get_session_model)],
) -> Runner:
    """Gets or creates a model-specific Runner instance.

    Args:
        request: The incoming FastAPI request object.
        config: The agent configuration.
        model_name: The model to use for this runner.

    Raises:
        HTTPException: If the runner fails to initialize.

    Returns:
        A model-specific Runner instance.
    """
    # Create unique runner for each model
    runner_key = f'runner_{model_name.replace("-", "_").replace(".", "_")}'

    if not hasattr(request.app.state, runner_key):
        try:
            # Get the model-specific agent from the factory
            agent = agent_factory.get_agent(model_name)

            # Create runner with the model-specific agent
            runner = Runner(
                agent=agent,
                app_name=config.app_name,
                session_service=request.app.state.session_service,
            )
            setattr(request.app.state, runner_key, runner)
            _logger.info(f'Created new Runner for model: {model_name}')
        except Exception as e:
            _logger.error(f'Failed to create runner for model {model_name}: %s', e)
            raise HTTPException(
                status_code=500,
                detail={
                    'message': (
                        f'Failed to initialize agent runner for model {model_name}'
                    ),
                    'error': str(e),
                },
            )
    return getattr(request.app.state, runner_key)
