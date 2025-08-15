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

"""Search service for querying indexed content.

This service leverages the indexing pipeline to provide semantic and keyword
search capabilities over blog content.
"""

from __future__ import annotations

from typing import Dict, Optional

from fastapi import HTTPException
from loguru import logger as _logger

from src.app.schemas import SearchQuery, SearchResponse
from src.indexing import IndexingPipeline, create_pipeline


class SearchService:
    """Service for handling search queries over indexed content."""

    def __init__(self):
        """Initialize the search service."""
        self._logger = _logger
        self._pipeline: Optional[IndexingPipeline] = None

    def _get_pipeline(self) -> IndexingPipeline:
        """Get or create the indexing pipeline instance.

        Returns:
            IndexingPipeline: The pipeline instance for searching.

        Raises:
            HTTPException: If the pipeline cannot be initialized.
        """
        if self._pipeline is None:
            try:
                self._pipeline = create_pipeline()
                self._logger.info('Initialized indexing pipeline for search')
            except Exception as e:
                self._logger.error(f'Failed to initialize indexing pipeline: {e}')
                raise HTTPException(
                    status_code=500,
                    detail={'message': 'Search service unavailable', 'error': str(e)},
                )
        return self._pipeline

    async def search_content(self, search_query: SearchQuery) -> SearchResponse:
        """Search content using the indexing pipeline.

        Args:
            search_query: The search query with parameters.

        Returns:
            SearchResponse: The search results and metadata.

        Raises:
            HTTPException: If search fails.
        """
        try:
            self._logger.info(
                f"Searching content with query: '{search_query.query}' "
                f'(mode: {search_query.search_type}, limit: {search_query.limit})'
            )

            pipeline = self._get_pipeline()

            # Perform the search using the unified search interface
            results = pipeline.search_unified(
                query=search_query.query,
                mode=search_query.search_type,
                limit=search_query.limit,
                category_filter=search_query.category_filter,
                similarity_threshold=search_query.similarity_threshold,
                case_sensitive=search_query.case_sensitive,
            )

            self._logger.info(
                f"Found {len(results)} results for query: '{search_query.query}'"
            )

            # Convert results to our response format
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        'title': result.get('title', 'Untitled'),
                        'category': result.get('category', 'unknown'),
                        'slug': result.get('slug', ''),
                        'excerpt': result.get('excerpt', ''),
                        'content': result.get('content', ''),
                        'score': result.get('score', 0.0),
                        'url': result.get('url', ''),
                        'publish_date': result.get('publish_date', ''),
                        'tags': result.get('tags', []),
                        'metadata': {
                            'distance': result.get('distance'),
                            'term_matches': result.get('term_matches'),
                        },
                    }
                )

            return SearchResponse(
                query=search_query.dict(),
                results=formatted_results,
                total_results=len(formatted_results),
                search_time_ms=0,  # Could add timing if needed
                metadata={
                    'search_type': search_query.search_type,
                    'threshold_applied': search_query.similarity_threshold,
                },
            )

        except Exception as e:
            self._logger.exception(f'Error during content search: {e}')
            raise HTTPException(
                status_code=500, detail={'message': 'Search failed', 'error': str(e)}
            )

    async def get_search_stats(self) -> Dict:
        """Get statistics about the search index.

        Returns:
            Dict: Statistics about indexed content.

        Raises:
            HTTPException: If stats retrieval fails.
        """
        try:
            self._logger.info('Retrieving search statistics')

            pipeline = self._get_pipeline()
            stats = pipeline.get_indexing_stats()

            self._logger.info('Successfully retrieved search statistics')
            return stats

        except Exception as e:
            self._logger.exception(f'Error retrieving search statistics: {e}')
            raise HTTPException(
                status_code=500,
                detail={
                    'message': 'Failed to retrieve search statistics',
                    'error': str(e),
                },
            )

    async def health_check(self) -> Dict:
        """Check the health of the search service.

        Returns:
            Dict: Health status information.
        """
        try:
            pipeline = self._get_pipeline()

            # Test with a simple query
            test_results = pipeline.search_unified(
                query='test',
                mode='semantic',
                limit=1,
            )

            return {
                'status': 'healthy',
                'pipeline_available': True,
                'database_available': pipeline.db is not None,
                'test_search_successful': True,
                'sample_results_count': len(test_results),
            }

        except Exception as e:
            self._logger.warning(f'Search service health check failed: {e}')
            return {'status': 'unhealthy', 'pipeline_available': False, 'error': str(e)}


# Global instance
search_service = SearchService()
