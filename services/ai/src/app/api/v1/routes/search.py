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

"""Search Router Module.

This module handles the routing and execution of content search endpoints.
It provides semantic and keyword search capabilities over indexed blog content.
"""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter
from loguru import logger as _logger

from src.app.schemas import SearchQuery, SearchResponse
from src.app.services.search_service import search_service

router = APIRouter()


@router.post('/', response_model=SearchResponse)
async def search_content(search_query: SearchQuery) -> SearchResponse:
    """Search indexed content using semantic or keyword search.

    Args:
        search_query: The search query with parameters including:
            - query: The search text
            - search_type: semantic, keyword, or hybrid
            - limit: Maximum results to return (1-100)
            - category_filter: Optional filter by blog/engineering
            - similarity_threshold: For semantic search (0.0-1.0)
            - case_sensitive: For keyword search

    Returns:
        SearchResponse: Contains search results with metadata.
    """
    _logger.info(
        f'Received search request: "{search_query.query}" '
        f'(type: {search_query.search_type}, limit: {search_query.limit})'
    )

    return await search_service.search_content(search_query)


@router.get('/stats')
async def get_search_stats() -> Dict:
    """Get statistics about the search index.

    Returns:
        Dict: Statistics including:
            - Total posts and chunks indexed
            - Content breakdown by category
            - Database information
            - Embedding model details
    """
    _logger.info('Retrieving search statistics')

    return await search_service.get_search_stats()


@router.get('/health')
async def search_health_check() -> Dict:
    """Check the health status of the search service.

    Returns:
        Dict: Health status information including:
            - Service status (healthy/unhealthy)
            - Pipeline availability
            - Database connectivity
            - Test search results
    """
    _logger.info('Performing search service health check')

    return await search_service.health_check()
