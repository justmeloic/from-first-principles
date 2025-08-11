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

"""Router for serving local files."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from loguru import logger as _logger

from src.app.core.config import settings

router = APIRouter()


@router.get('/{file_path:path}', response_class=FileResponse)
async def serve_local_file(request: Request, file_path: str):
    """Serves a file from the local testdata directory.

    This endpoint provides access to local files for development and testing
    purposes when FILE_ACCESS_METHOD is set to 'LOCAL'.

    Args:
        request: The FastAPI request object.
        file_path: The path to the file relative to the testdata directory.

    Returns:
        A FileResponse containing the requested file.

    Raises:
        HTTPException: If the file is not found or the path is invalid.
    """
    if settings.FILE_ACCESS_METHOD.lower() != 'local':
        _logger.warning(
            'Attempt to access local file endpoint while FILE_ACCESS_METHOD'
            " is not 'LOCAL'."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Local file access is disabled.',
        )

    try:
        base_dir = Path(settings.TESTDATA_DIR).resolve()
        full_path = (base_dir / file_path).resolve()

        # Security check: Ensure the resolved path is a child of the base directory.
        if not full_path.is_relative_to(base_dir):
            _logger.error('Directory traversal attempt detected: %s', file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid file path.',
            )

        if full_path.is_file():
            _logger.info('Serving local file: %s', full_path)
            return FileResponse(full_path)
        else:
            _logger.warning('Local file not found: %s', full_path)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='File not found'
            )
    except Exception as e:
        _logger.exception('Error serving local file %s: %s', file_path, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while serving the file.',
        )
