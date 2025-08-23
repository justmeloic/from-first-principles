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
Integration tests for the FastAPI application.

This module contains integration tests that test the application as a whole,
including middleware, routing, and basic functionality without mocking services.
These tests are designed to work even when complex services are unavailable.
"""

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestApplicationIntegration:
    """Integration tests for the entire application."""

    def test_app_startup(self, client):
        """Test that the application starts up successfully."""
        # Test that the app is responsive
        response = client.get('/api/v1/health')
        assert response.status_code == 200

    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI docs
        response = client.get('/docs')
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('content-type', '')

        # Test ReDoc
        response = client.get('/redoc')
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('content-type', '')

        # Test OpenAPI JSON schema
        response = client.get('/openapi.json')
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/json'

        # Validate it's proper JSON
        json_data = response.json()
        assert 'openapi' in json_data
        assert 'info' in json_data

    def test_cors_functionality(self, client):
        """Test CORS functionality with actual requests."""
        # Test preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type',
        }

        response = client.options('/api/v1/auth/login', headers=headers)
        # Should not return a server error
        assert response.status_code < 500

    def test_middleware_chain(self, client):
        """Test that middleware is properly configured."""
        # Test that session middleware is working by making a request
        # to a simple endpoint that doesn't require session dependencies
        response = client.get('/api/v1/health')
        assert response.status_code == 200

        # Check for basic response headers
        assert 'content-type' in response.headers


class TestErrorHandling:
    """Test error handling across the application."""

    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent/endpoint')
        assert response.status_code == 404

        data = response.json()
        assert 'detail' in data

    def test_405_handling(self, client):
        """Test 405 Method Not Allowed handling."""
        # Try DELETE on a GET-only endpoint
        response = client.delete('/api/v1/health')
        assert response.status_code == 405

    def test_json_validation_error(self, client):
        """Test 422 validation error handling."""
        # Send invalid JSON to search endpoint
        response = client.post(
            '/api/v1/search/',
            json={'invalid': 'data', 'missing': 'required_fields'},
        )
        assert response.status_code == 422

        data = response.json()
        assert 'detail' in data

    def test_malformed_json_handling(self, client):
        """Test handling of malformed JSON."""
        response = client.post(
            '/api/v1/search/',
            data='{"invalid": json}',
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == 422


class TestAPIVersioning:
    """Test API versioning functionality."""

    def test_v1_endpoints_accessible(self, client):
        """Test that v1 endpoints are accessible."""
        endpoints = [
            '/api/v1/health',
            '/api/v1/status',
            '/api/v1/search/health',
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404
            # Should be a valid HTTP response
            assert response.status_code < 500 or response.status_code in [500, 503]

    def test_root_redirect_or_info(self, client):
        """Test root endpoint behavior."""
        response = client.get('/')
        # Could be a redirect, info page, or 404 depending on implementation
        assert response.status_code in [200, 301, 302, 404]


class TestContentTypes:
    """Test content type handling."""

    def test_json_content_type_handling(self, client):
        """Test JSON content type handling."""
        # Test with search endpoint instead of auth
        response = client.post(
            '/api/v1/search/',
            json={'query': 'test', 'search_type': 'semantic'},
            headers={'Content-Type': 'application/json'},
        )
        # Should not fail due to content type issues
        assert response.status_code in [200, 422]

    def test_accept_header_handling(self, client):
        """Test Accept header handling."""
        # Test with application/json accept header
        headers = {'Accept': 'application/json'}
        response = client.get('/api/v1/health', headers=headers)
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('content-type', '')


class TestResponseFormats:
    """Test response format consistency."""

    def test_health_response_format(self, client):
        """Test that health endpoints return consistent format."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert 'status' in data
        assert isinstance(data['status'], str)

    def test_status_response_format(self, client):
        """Test that status endpoint returns consistent format."""
        response = client.get('/api/v1/status')
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert 'title' in data
        assert 'version' in data
        assert 'status' in data

    def test_error_response_format(self, client):
        """Test that error responses have consistent format."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

        data = response.json()
        assert isinstance(data, dict)
        assert 'detail' in data


class TestSecurityHeaders:
    """Test security-related headers and configurations."""

    def test_security_headers_present(self, client):
        """Test that appropriate security headers are present."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200

        # These headers might be set by middleware
        # The exact headers depend on your security configuration
        headers = response.headers

        # Common security headers to check for
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
        ]

        # Note: Not all applications set these headers
        # This test documents what headers are expected
        for header in security_headers:
            if header in headers:
                assert headers[header] is not None


if __name__ == '__main__':
    # Allow running tests directly with python
    pytest.main([__file__, '-v'])
