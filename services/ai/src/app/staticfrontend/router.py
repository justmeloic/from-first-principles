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
Router for serving the static frontend application.

This module handles the logic for serving a static build of a web application,
including mounting static asset directories and providing fallback routing
for single-page applications (SPAs).
"""

from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

frontend_router = APIRouter()

static_files_dir = Path(__file__).parent.parent.parent.parent / 'build/static_frontend'


def register_frontend_routes(app: FastAPI):
    """
    Registers all routes necessary to serve the frontend application.

    This function checks if the frontend build exists and then configures
    the necessary routes and static file mounts on the main FastAPI app instance.

    Args:
        app: The main FastAPI application instance.
    """
    if not static_files_dir.is_dir():
        # If the frontend directory doesn't exist, register a simple root endpoint
        # and log a warning.
        @app.get('/')
        async def root():
            return {
                'message': 'API is running. Frontend not found.',
                'docs_url': '/docs',
            }

        return  # Stop further frontend route registration

    app.mount(
        '/_next',
        StaticFiles(directory=static_files_dir / '_next'),
        name='next-static-assets',
    )

    # Serve the root index.html
    @frontend_router.get('/', response_class=FileResponse, include_in_schema=False)
    async def serve_root_index() -> FileResponse:
        """Serves the main index.html file for the root path."""
        index_path = static_files_dir / 'index.html'
        if not index_path.is_file():
            raise HTTPException(status_code=404, detail='Frontend index.html not found')
        return FileResponse(index_path)

    # Catch-all route to serve other frontend files or the main index.html
    @frontend_router.get('/{full_path:path}', response_class=FileResponse)
    async def serve_spa(full_path: str) -> FileResponse:
        """
        Serves static files for the SPA or falls back to index.html.

        This allows the client-side router to handle application navigation.
        """
        # First, check for a direct file match (e.g., for assets)
        file_path = static_files_dir / full_path
        if file_path.is_file() and full_path != 'index.html':
            return FileResponse(file_path)

        # Next, check for an HTML file with the same name as the path
        html_path = static_files_dir / f'{full_path}.html'
        if html_path.is_file():
            return FileResponse(html_path)

        # Fallback to serving the main index.html for SPA routing
        index_html_path = static_files_dir / 'index.html'
        if index_html_path.is_file():
            return FileResponse(index_html_path)

        raise HTTPException(status_code=404, detail='Not Found')

    app.include_router(frontend_router)
