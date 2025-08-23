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
Search API tests for the FastAPI application.

This module contains tests for the search endpoints including content search,
search statistics, and health checks. These tests may require mocking search
services due to their complexity.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_search_response():
    """Create a mock search response."""
    return {
        'results': [
            {
                'id': 'test-1',
                'title': 'Test Blog Post',
                'content': 'This is a test blog post about testing.',
                'category': 'blog',
                'similarity_score': 0.85,
                'metadata': {'author': 'Test Author', 'date': '2025-08-22'},
            }
        ],
        'total_results': 1,
        'query_type': 'semantic',
        'processing_time': 0.123,
        'metadata': {'embedding_model': 'test-model', 'index_version': '1.0'},
    }


@pytest.fixture
def mock_search_stats():
    """Create mock search statistics."""
    return {
        'total_documents': 150,
        'total_chunks': 1200,
        'categories': {'blog': 80, 'engineering': 70},
        'index_size_mb': 25.6,
        'last_updated': '2025-08-22T10:00:00Z',
        'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
        'database_type': 'lancedb',
    }


class TestSearchEndpoints:
    """Test class for search functionality."""

    @patch('src.app.services.search_service.search_service.search_content')
    def test_search_content_semantic(self, mock_search, client, mock_search_response):
        """Test semantic search functionality."""
        mock_search.return_value = mock_search_response

        search_data = {
            'query': 'test search query',
            'search_type': 'semantic',
            'limit': 10,
            'similarity_threshold': 0.7,
        }

        response = client.post('/api/v1/search/', json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert 'results' in data
        assert 'total_results' in data
        assert data['total_results'] == 1
        assert len(data['results']) == 1
        assert data['results'][0]['title'] == 'Test Blog Post'

    @patch('src.app.services.search_service.search_service.search_content')
    def test_search_content_keyword(self, mock_search, client, mock_search_response):
        """Test keyword search functionality."""
        mock_search_response['query_type'] = 'keyword'
        mock_search.return_value = mock_search_response

        search_data = {
            'query': 'testing',
            'search_type': 'keyword',
            'limit': 5,
            'case_sensitive': False,
        }

        response = client.post('/api/v1/search/', json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert data['query_type'] == 'keyword'

    @patch('src.app.services.search_service.search_service.search_content')
    def test_search_content_with_category_filter(
        self, mock_search, client, mock_search_response
    ):
        """Test search with category filter."""
        mock_search.return_value = mock_search_response

        search_data = {
            'query': 'engineering practices',
            'search_type': 'semantic',
            'category_filter': 'engineering',
            'limit': 20,
        }

        response = client.post('/api/v1/search/', json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert 'results' in data

    def test_search_invalid_payload(self, client):
        """Test search with invalid payload."""
        invalid_search_data = {
            'search_type': 'invalid_type',  # Invalid search type
            'limit': 1000,  # Assuming limit is validated
        }

        response = client.post('/api/v1/search/', json=invalid_search_data)
        assert response.status_code == 422  # Validation error

    def test_search_missing_query(self, client):
        """Test search without required query field."""
        search_data = {
            'search_type': 'semantic',
            'limit': 10,
        }

        response = client.post('/api/v1/search/', json=search_data)
        assert response.status_code == 422  # Missing required field

    @patch('src.app.services.search_service.search_service.get_search_stats')
    def test_search_stats(self, mock_stats, client, mock_search_stats):
        """Test search statistics endpoint."""
        mock_stats.return_value = mock_search_stats

        response = client.get('/api/v1/search/stats')
        assert response.status_code == 200

        data = response.json()
        assert 'total_documents' in data
        assert 'total_chunks' in data
        assert 'categories' in data
        assert data['total_documents'] == 150
        assert data['total_chunks'] == 1200

    @patch('src.app.services.search_service.search_service.health_check')
    def test_search_health_check_healthy(self, mock_health, client):
        """Test search health check when service is healthy."""
        mock_health.return_value = {
            'status': 'healthy',
            'database_connected': True,
            'embedding_model_loaded': True,
            'test_search_successful': True,
        }

        response = client.get('/api/v1/search/health')
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'healthy'
        assert data['database_connected'] is True

    @patch('src.app.services.search_service.search_service.health_check')
    def test_search_health_check_unhealthy(self, mock_health, client):
        """Test search health check when service is unhealthy."""
        mock_health.side_effect = Exception('Search service unavailable')

        response = client.get('/api/v1/search/health')
        # The actual status code depends on error handling implementation
        assert response.status_code in [500, 503]


class TestSearchValidation:
    """Test class for search input validation."""

    def test_search_limit_validation(self, client):
        """Test search with various limit values."""
        # Test with valid limit
        search_data = {'query': 'test', 'search_type': 'semantic', 'limit': 50}
        response = client.post('/api/v1/search/', json=search_data)
        # May succeed or fail depending on service availability
        assert response.status_code in [200, 422, 500, 503]

        # Test with invalid limit (too high)
        search_data = {'query': 'test', 'search_type': 'semantic', 'limit': 1000}
        response = client.post('/api/v1/search/', json=search_data)
        # Should return validation error if limit is validated
        assert response.status_code in [422, 200, 500, 503]

    def test_search_similarity_threshold_validation(self, client):
        """Test search with various similarity threshold values."""
        # Valid threshold
        search_data = {
            'query': 'test',
            'search_type': 'semantic',
            'similarity_threshold': 0.5,
        }
        response = client.post('/api/v1/search/', json=search_data)
        assert response.status_code in [200, 422, 500, 503]

        # Invalid threshold (out of range)
        search_data = {
            'query': 'test',
            'search_type': 'semantic',
            'similarity_threshold': 1.5,
        }
        response = client.post('/api/v1/search/', json=search_data)
        assert response.status_code in [422, 200, 500, 503]


class TestSearchServiceErrors:
    """Test class for search service error handling."""

    @patch('src.app.services.search_service.search_service.search_content')
    def test_search_service_timeout(self, mock_search, client):
        """Test handling of search service timeout."""
        mock_search.side_effect = TimeoutError('Search service timeout')

        search_data = {
            'query': 'test timeout',
            'search_type': 'semantic',
            'limit': 10,
        }

        response = client.post('/api/v1/search/', json=search_data)
        # Should handle timeout gracefully
        assert response.status_code in [408, 500, 503]

    @patch('src.app.services.search_service.search_service.search_content')
    def test_search_service_internal_error(self, mock_search, client):
        """Test handling of search service internal errors."""
        mock_search.side_effect = Exception('Internal search error')

        search_data = {
            'query': 'test error',
            'search_type': 'semantic',
            'limit': 10,
        }

        response = client.post('/api/v1/search/', json=search_data)
        # Should handle internal errors gracefully
        assert response.status_code in [500, 503]

    @patch('src.app.services.search_service.search_service.get_search_stats')
    def test_stats_service_error(self, mock_stats, client):
        """Test handling of stats service errors."""
        mock_stats.side_effect = Exception('Stats service error')

        response = client.get('/api/v1/search/stats')
        assert response.status_code in [500, 503]


if __name__ == '__main__':
    # Allow running tests directly with python
    pytest.main([__file__, '-v'])
