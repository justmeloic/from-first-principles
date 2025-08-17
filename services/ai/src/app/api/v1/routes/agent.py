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

import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from google.genai import types as genai_types
from loguru import logger as _logger

from src.agents.agent_factory import agent_factory
from src.app.artifacts.file_validator import FileValidator
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


async def _save_file_as_artifact(
    request: Request, file: UploadFile, config: AgentConfig
) -> str:
    """Save an uploaded file as an artifact and return its filename."""
    import time

    # Generate unique filename for this upload
    original_filename = file.filename or 'unknown'
    # Use timestamp  uuid to ensure uniqueness
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    artifact_filename = f'{timestamp}_{unique_id}_{original_filename}'

    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset file pointer

    # Detect MIME type

    validator = FileValidator()
    mime_type = validator._detect_mime_type(original_filename, content)

    # Create artifact Part using the recommended ADK convenience method
    artifact = genai_types.Part.from_bytes(data=content, mime_type=mime_type)

    # Get session information
    session_id = getattr(request.state, 'actual_session_id', 'default')

    # Get artifact service from app state
    artifact_service = request.app.state.artifact_service

    # Save artifact
    await artifact_service.save_artifact(
        app_name=config.app_name,
        user_id=config.user_id,
        session_id=session_id,
        filename=artifact_filename,
        artifact=artifact,
    )

    return artifact_filename


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
    config: Annotated[AgentConfig, Depends(get_agent_config)],
    text: str = Form(''),  # Allow empty text
    model: str | None = Form(None),
    files: list[UploadFile] | None = File(None),
) -> AgentResponse:
    """
    Unified endpoint: processes user message with optional file attachments.

    Files are saved as artifacts and immediately available to the agent.

    Args:
        request: The incoming FastAPI request object.
        response: The outgoing FastAPI response object.
        text: The user's query text as form field (can be empty if files provided).
        model: Optional model selection as form field.
        files: Optional list of uploaded files.
        config: The agent configuration, injected as a dependency.

    Returns:
        An AgentResponse object containing the agent's response and metadata.

    Raises:
        HTTPException: If the request contains neither text nor files, or if
          the uploaded files fail validation.
    """
    # Validate that we have either text or files
    if not text.strip() and not files:
        raise HTTPException(
            status_code=400,
            detail='Must provide either text message or file attachments',
        )

    # Create Query object from form data
    query = Query(text=text, model=model)
    # Set the selected model in request state for dependencies to use
    request.state.selected_model = query.model

    # Get dependencies with model-specific configurations
    session = await get_or_create_session(request, response, config)
    model_name = await get_session_model(request)
    runner = get_runner(request, config, model_name)

    _logger.info('Received query for model %s: %s...', model_name, query.text[:50])

    # Handle file uploads if present
    uploaded_artifacts = []
    if files:
        validator = FileValidator()
        is_valid, validation_errors = await validator.validate_files(files)

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    'message': 'File validation failed',
                    'errors': validation_errors,
                },
            )

        # Save valid files as artifacts
        for file in files:
            artifact_id = await _save_file_as_artifact(request, file, config)
            uploaded_artifacts.append(artifact_id)
            _logger.info(f'Saved file {file.filename} as artifact {artifact_id}')

    # Add file references to query context
    if uploaded_artifacts:
        query.file_artifacts = uploaded_artifacts

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
