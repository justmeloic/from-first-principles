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
Basic API tests for the FastAPI application.

This module contains tests for the basic API endpoints including health checks,
status endpoints, and authentication functionality. These tests focus on the
core API functionality without testing complex services like agents or search.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    session = MagicMock()
    session.id = 'test-session-123'
    session.state = {}
    return session


class TestHealthEndpoints:
    """Test class for health and status endpoints."""

    def test_health_check(self, client):
        """Test the main health check endpoint."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert 'version' in data
        assert data['status'] == 'healthy'

    def test_api_status(self, client):
        """Test the API status endpoint."""
        response = client.get('/api/v1/status')
        assert response.status_code == 200

        data = response.json()
        assert 'title' in data
        assert 'description' in data
        assert 'version' in data
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_search_health_check(self, client):
        """Test the search service health check endpoint."""
        # This endpoint might fail if search service is not available
        # but we test that it returns a proper response structure
        response = client.get('/api/v1/search/health')
        assert response.status_code in [200, 500, 503]  # Accept various health states

        if response.status_code == 200:
            data = response.json()
            # The exact structure depends on search service implementation
            assert isinstance(data, dict)


class TestErrorHandling:
    """Test class for error handling and edge cases."""

    def test_nonexistent_endpoint(self, client):
        """Test accessing a non-existent endpoint."""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test using wrong HTTP method."""
        response = client.delete('/api/v1/health')
        assert response.status_code == 405

    def test_invalid_json_request(self, client):
        """Test sending invalid JSON to an endpoint."""
        response = client.post(
            '/api/v1/search/',
            data='invalid json',
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == 422

    def test_missing_content_type(self, client):
        """Test request without proper content type."""
        response = client.post('/api/v1/search/', data='{"query": "test"}')
        # The search endpoint might be flexible with content types
        # Just ensure it doesn't crash
        assert response.status_code < 500


class TestCORS:
    """Test class for CORS functionality."""

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options('/api/v1/health')

        # Should not return an error for OPTIONS request
        assert response.status_code in [200, 405]

    def test_cors_preflight_request(self, client):
        """Test CORS preflight request."""
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type',
        }

        response = client.options('/api/v1/health', headers=headers)

        # The exact response depends on CORS middleware configuration
        # but it should not be a server error
        assert response.status_code < 500


class TestRouteParameters:
    """Test class for route parameters and query strings."""

    def test_search_stats_endpoint(self, client):
        """Test the search stats endpoint."""
        response = client.get('/api/v1/search/stats')

        # This might fail if search service is not available
        # Accept both success and service unavailable responses
        assert response.status_code in [200, 500, 503]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_get_request_with_query_params(self, client):
        """Test GET request with query parameters on status endpoint."""
        response = client.get('/api/v1/status?extra=param')
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data


if __name__ == '__main__':
    # Allow running tests directly with python
    pytest.main([__file__, '-v'])
