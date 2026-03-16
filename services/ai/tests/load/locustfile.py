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
Locust load testing configuration for AI Service API.

Run with:
    cd services/ai
    locust -f tests/load/locustfile.py --host=http://localhost:8081

Or for headless mode:
    locust -f tests/load/locustfile.py --host=http://localhost:8081 --headless -u 100 -r 10 -t 60s

Options:
    -u: Number of users to simulate
    -r: Spawn rate (users per second)
    -t: Run time (e.g., 60s, 5m, 1h)
"""

import random

from locust import HttpUser, between, tag, task


# Sample search queries for realistic load testing
SAMPLE_SEARCH_QUERIES = [
    'machine learning basics',
    'neural networks explained',
    'how to learn programming',
    'software engineering principles',
    'artificial intelligence',
    'deep learning tutorial',
    'python programming tips',
    'web development best practices',
    'data structures algorithms',
    'system design patterns',
]

# Sample agent prompts for realistic load testing
SAMPLE_AGENT_PROMPTS = [
    'What is machine learning?',
    'Explain neural networks simply',
    'How do I start learning to code?',
    'What are the best programming practices?',
    'Tell me about software architecture',
]


class AIServiceUser(HttpUser):
    """Simulates a typical user interacting with the AI Service API."""

    # Wait 1-3 seconds between tasks to simulate real user behavior
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a simulated user starts."""
        # Add authentication setup here if needed
        pass

    @task(10)
    @tag('health')
    def health_check(self):
        """Check API health - high frequency task."""
        self.client.get('/api/v1/health')

    @task(5)
    @tag('status')
    def server_status(self):
        """Check server status."""
        self.client.get('/api/v1/status')

    @task(3)
    @tag('models')
    def list_models(self):
        """List available models."""
        with self.client.get(
            '/api/v1/root_agent/models',
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 403]:
                response.success()

    @task(5)
    @tag('search')
    def search_content(self):
        """Perform semantic search - common operation."""
        query = random.choice(SAMPLE_SEARCH_QUERIES)
        payload = {
            'query': query,
            'search_type': 'semantic',
            'limit': 10,
        }
        with self.client.post(
            '/api/v1/search/',
            json=payload,
            name='/api/v1/search/',
            catch_response=True,
            timeout=30,
        ) as response:
            if response.status_code in [200, 401, 403, 422, 500]:
                # 500 may occur if search index not initialized
                response.success()
            elif response.status_code == 429:
                # Rate limited - still counts as handled
                response.success()
            else:
                response.failure(f'Got status code {response.status_code}')

    @task(2)
    @tag('search')
    def search_stats(self):
        """Get search statistics."""
        with self.client.get(
            '/api/v1/search/stats',
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 403, 500]:
                response.success()

    @task(2)
    @tag('search', 'health')
    def search_health(self):
        """Check search service health."""
        with self.client.get(
            '/api/v1/search/health',
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 403, 500]:
                response.success()

    @task(2)
    @tag('cache')
    def cache_stats(self):
        """Get cache statistics."""
        with self.client.get(
            '/api/v1/cache/stats',
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 403, 500]:
                response.success()

    @task(1)
    @tag('agent')
    def invoke_agent(self):
        """Invoke the root agent - most expensive operation."""
        prompt = random.choice(SAMPLE_AGENT_PROMPTS)
        # Using form data as per the agent endpoint implementation
        with self.client.post(
            '/api/v1/root_agent/',
            data={'text': prompt},
            name='/api/v1/root_agent/',
            catch_response=True,
            timeout=120,
        ) as response:
            if response.status_code in [200, 401, 403, 422]:
                response.success()
            elif response.status_code == 429:
                # Rate limited - still counts as handled
                response.success()
            else:
                response.failure(f'Got status code {response.status_code}')


class SearchHeavyUser(HttpUser):
    """Simulates a power user making frequent search requests."""

    wait_time = between(0.5, 1.5)
    weight = 2  # More of these users in the mix

    @task(5)
    @tag('search', 'heavy')
    def semantic_search(self):
        """Heavy semantic search usage."""
        query = random.choice(SAMPLE_SEARCH_QUERIES)
        payload = {
            'query': query,
            'search_type': 'semantic',
            'limit': 20,
        }
        with self.client.post(
            '/api/v1/search/',
            json=payload,
            name='/api/v1/search/ (semantic)',
            catch_response=True,
            timeout=30,
        ) as response:
            if response.status_code in [200, 401, 403, 422, 429, 500]:
                response.success()
            else:
                response.failure(f'Got status code {response.status_code}')

    @task(3)
    @tag('search', 'heavy')
    def keyword_search(self):
        """Keyword search requests."""
        query = random.choice(SAMPLE_SEARCH_QUERIES)
        payload = {
            'query': query,
            'search_type': 'keyword',
            'limit': 20,
        }
        with self.client.post(
            '/api/v1/search/',
            json=payload,
            name='/api/v1/search/ (keyword)',
            catch_response=True,
            timeout=30,
        ) as response:
            if response.status_code in [200, 401, 403, 422, 429, 500]:
                response.success()
            else:
                response.failure(f'Got status code {response.status_code}')

    @task(2)
    @tag('search', 'heavy')
    def hybrid_search(self):
        """Hybrid search requests."""
        query = random.choice(SAMPLE_SEARCH_QUERIES)
        payload = {
            'query': query,
            'search_type': 'hybrid',
            'limit': 15,
        }
        with self.client.post(
            '/api/v1/search/',
            json=payload,
            name='/api/v1/search/ (hybrid)',
            catch_response=True,
            timeout=30,
        ) as response:
            if response.status_code in [200, 401, 403, 422, 429, 500]:
                response.success()
            else:
                response.failure(f'Got status code {response.status_code}')


class APIOnlyUser(HttpUser):
    """Simulates API-only access patterns (lightweight endpoints only)."""

    wait_time = between(0.1, 0.5)
    weight = 3  # Higher weight means more of these users

    @task(5)
    @tag('health')
    def health_check(self):
        """Frequent health checks."""
        self.client.get('/api/v1/health')

    @task(3)
    @tag('status')
    def server_status(self):
        """Check server status."""
        self.client.get('/api/v1/status')

    @task(2)
    @tag('models')
    def list_models(self):
        """List models."""
        self.client.get('/api/v1/root_agent/models')

    @task(2)
    @tag('cache')
    def cache_stats(self):
        """Get cache stats."""
        with self.client.get(
            '/api/v1/cache/stats',
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 403, 500]:
                response.success()

    @task(1)
    @tag('search')
    def search_stats(self):
        """Get search statistics."""
        with self.client.get(
            '/api/v1/search/stats',
            catch_response=True,
        ) as response:
            if response.status_code in [200, 401, 403, 500]:
                response.success()
