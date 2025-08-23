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
Test configuration and fixtures for the FastAPI test suite.

This module provides common test configurations, fixtures, and utilities
that can be shared across multiple test files.
"""

import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing the app
os.environ['ENVIRONMENT'] = 'test'
os.environ['LOG_LEVEL'] = 'WARNING'  # Reduce logging during tests

from src.app.main import app


@pytest.fixture(scope='session')
def test_settings():
    """Provide test-specific settings."""
    return {
        'api_title': 'AgentChat API',
        'api_version': '1.0.0',
        'environment': 'test',
    }


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


@pytest.fixture
def search_query_semantic():
    """Provide a valid semantic search query."""
    return {
        'query': 'artificial intelligence and machine learning',
        'search_type': 'semantic',
        'limit': 10,
        'similarity_threshold': 0.7,
    }


@pytest.fixture
def search_query_keyword():
    """Provide a valid keyword search query."""
    return {
        'query': 'python programming',
        'search_type': 'keyword',
        'limit': 5,
        'case_sensitive': False,
    }


@pytest.fixture
def mock_search_results():
    """Mock search results for testing."""
    return {
        'results': [
            {
                'id': 'post-1',
                'title': 'Introduction to AI',
                'content': 'Artificial intelligence is transforming...',
                'category': 'blog',
                'similarity_score': 0.92,
                'metadata': {
                    'author': 'John Doe',
                    'date': '2025-08-15',
                    'tags': ['ai', 'technology'],
                },
            },
            {
                'id': 'post-2',
                'title': 'Machine Learning Basics',
                'content': 'Machine learning algorithms can learn...',
                'category': 'engineering',
                'similarity_score': 0.87,
                'metadata': {
                    'author': 'Jane Smith',
                    'date': '2025-08-20',
                    'tags': ['ml', 'algorithms'],
                },
            },
        ],
        'total_results': 2,
        'query_type': 'semantic',
        'processing_time': 0.156,
        'metadata': {
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'index_version': '1.2.0',
        },
    }


class TestConstants:
    """Constants for testing."""

    TEST_SESSION_ID = 'test-session-123'
    TEST_USER_NAME = 'Test User'


class MockServices:
    """Mock service responses."""

    @staticmethod
    def healthy_status():
        """Return a healthy status response."""
        return {'status': 'healthy', 'version': '1.0.0'}

    @staticmethod
    def search_stats():
        """Return mock search statistics."""
        return {
            'total_documents': 250,
            'total_chunks': 2000,
            'categories': {'blog': 120, 'engineering': 130},
            'index_size_mb': 45.3,
            'last_updated': '2025-08-22T09:30:00Z',
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'database_type': 'lancedb',
        }

    @staticmethod
    def search_health():
        """Return healthy search service status."""
        return {
            'status': 'healthy',
            'database_connected': True,
            'embedding_model_loaded': True,
            'test_search_successful': True,
            'last_health_check': '2025-08-22T10:00:00Z',
        }
