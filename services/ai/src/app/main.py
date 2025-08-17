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

"""
Main FastAPI application entry point.

This module contains the core FastAPI application setup for the Agent
Orchestration service. It handles application configuration, middleware setup,
routing, and serves both API endpoints and static frontend files. The
application integrates with Google Cloud Platform services and provides session
management capabilities.

Features:
- RESTful API endpoints for agent orchestration
- Static file serving for frontend applications
- CORS middleware for cross-origin requests
- Session management with in-memory storage
- Health check endpoints
- Comprehensive logging setup
- GCP environment configuration
"""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from loguru import logger as _logger

from src.app.api.v1.endpoints import main_v1_router
from src.app.core.config import settings
from src.app.core.logging import setup_logging
from src.app.middleware.session_middleware import SessionMiddleware
from src.app.staticfrontend.router import register_frontend_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.

    This async context manager manages the application lifecycle, performing
    necessary setup during startup and cleanup during shutdown. It configures
    logging, validates GCP environment, and initializes the session service.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded back to the application during its runtime.

    Note:
        This function is called automatically by FastAPI during application
        startup and shutdown phases.
    """
    setup_logging()
    _logger.info('Starting AI Backend API...')

    app.state.session_service = InMemorySessionService()
    app.state.artifact_service = InMemoryArtifactService()
    _logger.info('Initialized in memory ( artifact & session) services')

    yield
    _logger.info('Shutting down Agent Orchestration API...')


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, **settings.cors.model_dump())
app.add_middleware(SessionMiddleware)

main_router = APIRouter()
main_router.include_router(main_v1_router)

app.include_router(main_router)


register_frontend_routes(app)
