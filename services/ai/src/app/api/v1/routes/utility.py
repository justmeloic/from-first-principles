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

"""Utility Router Module.

This module provides utility endpoints for development and PoC purposes.
These endpoints are not intended for production use and should be used with caution.
"""

import subprocess

from fastapi import APIRouter, HTTPException
from loguru import logger as _logger

from src.app.core.config import settings

router = APIRouter()


@router.post('/restart')
async def restart_server():
    """
    Restarts the Uvicorn server by executing an external shell script.
    **Warning:** For internal PoC use only. Not secure for production.
    """
    _logger.warning('Restart endpoint triggered. This is for PoC use only.')
    try:
        script_path = settings.RESTART_SCRIPT_PATH
        _logger.info(f'Executing restart script: {script_path}')
        subprocess.Popen([script_path])
        return {'message': 'Server is restarting...'}
    except Exception as e:
        _logger.exception(f'Failed to execute restart script: {e}')
        raise HTTPException(
            status_code=500,
            detail=f'Failed to execute restart script: {e}',
        )


@router.get('/status', tags=['Server Info'])
async def api_status() -> dict[str, str]:
    """Provides API information and health status."""
    _logger.info('API status requested.')
    return {
        'title': settings.API_TITLE,
        'description': settings.API_DESCRIPTION,
        'version': settings.API_VERSION,
        'status': 'healthy',
    }


@router.get('/health')
async def health_check():
    """
    Health check endpoint for application monitoring.

    Provides a simple health status check that can be used by load balancers,
    monitoring systems, or deployment pipelines to verify that the application
    is running and responsive.

    Returns:
        dict: A dictionary containing the application status and version.
            - status (str): Always "healthy" when the endpoint is reachable
            - version (str): The current API version from settings

    Example:
        GET /health
        Response: {"status": "healthy", "version": "1.0.0"}
    """
    _logger.info('Health check requested.')
    return {'status': 'healthy', 'version': settings.API_VERSION}


@router.get('/cache/stats', tags=['Cache'])
async def get_cache_stats():
    """
    Get semantic cache statistics.

    Returns statistics about the semantic similarity cache including:
    - Total queries processed
    - Cache hits and misses
    - Hit rate percentage
    - Average latencies for hits and misses
    - Current cache size and configuration

    Returns:
        dict: Cache statistics including hit rate, entry count, and configuration.

    Example:
        GET /cache/stats
        Response: {
            "enabled": true,
            "similarity_threshold": 0.92,
            "total_queries": 100,
            "cache_hits": 35,
            "cache_misses": 65,
            "hit_rate_percent": 35.0,
            "total_entries": 50,
            ...
        }
    """
    from src.app.services.semantic_cache import get_semantic_cache

    _logger.info('Cache stats requested.')
    try:
        cache = get_semantic_cache()
        return cache.get_stats()
    except Exception as e:
        _logger.error(f'Failed to get cache stats: {e}')
        raise HTTPException(
            status_code=500,
            detail=f'Failed to get cache stats: {e}',
        )


@router.delete('/cache/clear', tags=['Cache'])
async def clear_cache(model_name: str = None):
    """
    Clear the semantic cache.

    Optionally clear only entries for a specific model. If no model_name is provided,
    all cache entries will be cleared.

    Args:
        model_name: Optional model name to clear entries for (e.g., "gemini-2.5-flash").
                   If not provided, clears the entire cache.

    Returns:
        dict: Information about the cleared cache entries.

    Example:
        DELETE /cache/clear
        Response: {"cleared_entries": 50, "message": "Cache cleared successfully"}

        DELETE /cache/clear?model_name=gemini-2.5-flash
        Response: {"cleared_entries": 25, "message": "Cache cleared for model: gemini-2.5-flash"}
    """
    from src.app.services.semantic_cache import get_semantic_cache

    _logger.warning(f'Cache clear requested. model_name={model_name}')
    try:
        cache = get_semantic_cache()
        cleared_count = await cache.clear(model_name=model_name)

        message = (
            f'Cache cleared for model: {model_name}'
            if model_name
            else 'Cache cleared successfully'
        )

        return {
            'cleared_entries': cleared_count,
            'message': message,
        }
    except Exception as e:
        _logger.error(f'Failed to clear cache: {e}')
        raise HTTPException(
            status_code=500,
            detail=f'Failed to clear cache: {e}',
        )
