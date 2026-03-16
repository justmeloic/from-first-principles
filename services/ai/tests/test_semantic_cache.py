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

"""Unit tests for the semantic similarity cache service.

These tests use mocks to isolate the cache logic from external dependencies
(LanceDB and SentenceTransformer).
"""

import hashlib
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.app.services.semantic_cache import CacheEntry, CacheStats, SemanticCache


class TestCacheStats:
    """Tests for CacheStats dataclass."""

    def test_hit_rate_zero_queries(self):
        """Hit rate should be 0 when no queries have been made."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Hit rate should correctly calculate percentage."""
        stats = CacheStats(total_queries=100, cache_hits=35, cache_misses=65)
        assert stats.hit_rate == 35.0

    def test_hit_rate_all_hits(self):
        """Hit rate should be 100% when all queries are hits."""
        stats = CacheStats(total_queries=50, cache_hits=50, cache_misses=0)
        assert stats.hit_rate == 100.0


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """CacheEntry should store all required fields."""
        entry = CacheEntry(
            query="What is Python?",
            response="Python is a programming language.",
            model_name="gemini-2.5-flash",
            similarity_score=0.95,
            created_at=datetime.now(),
        )
        assert entry.query == "What is Python?"
        assert entry.response == "Python is a programming language."
        assert entry.model_name == "gemini-2.5-flash"
        assert entry.similarity_score == 0.95
        assert entry.hit_count == 0


class TestSemanticCache:
    """Tests for SemanticCache class."""

    @pytest.fixture
    def mock_sentence_transformer(self):
        """Create a mock SentenceTransformer."""
        mock = MagicMock()
        mock.get_sentence_embedding_dimension.return_value = 384
        mock.max_seq_length = 512
        mock.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)
        return mock

    @pytest.fixture
    def mock_lancedb(self):
        """Create a mock LanceDB connection."""
        mock_table = MagicMock()
        mock_table.to_pandas.return_value = MagicMock(__len__=lambda self: 0)
        mock_table.search.return_value = mock_table
        mock_table.where.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.to_list.return_value = []

        mock_db = MagicMock()
        mock_db.table_names.return_value = []
        mock_db.create_table.return_value = mock_table
        mock_db.open_table.return_value = mock_table

        return mock_db, mock_table

    @pytest.fixture
    def cache_with_mocks(self, mock_sentence_transformer, mock_lancedb):
        """Create a SemanticCache with mocked dependencies."""
        mock_db, mock_table = mock_lancedb

        with patch(
            'src.app.services.semantic_cache.SENTENCE_TRANSFORMERS_AVAILABLE', True
        ), patch(
            'src.app.services.semantic_cache.LANCEDB_AVAILABLE', True
        ), patch(
            'src.app.services.semantic_cache.SentenceTransformer',
            return_value=mock_sentence_transformer,
        ), patch(
            'src.app.services.semantic_cache.lancedb'
        ) as mock_lance:
            mock_lance.connect.return_value = mock_db

            cache = SemanticCache(
                similarity_threshold=0.92,
                enabled=True,
                db_path='/tmp/test_cache',
            )

            # Replace the table with our mock
            cache.cache_table = mock_table
            cache.db = mock_db

            return cache, mock_sentence_transformer, mock_table

    def test_cache_disabled(self):
        """Cache should not initialize when disabled."""
        cache = SemanticCache(enabled=False)
        assert cache.enabled is False
        assert cache.embedding_model is None

    def test_cache_initialization(self, cache_with_mocks):
        """Cache should initialize with correct configuration."""
        cache, _, _ = cache_with_mocks
        assert cache.enabled is True
        assert cache.similarity_threshold == 0.92
        assert cache.embedding_dim == 384

    def test_generate_embedding(self, cache_with_mocks):
        """Embedding generation should call the model correctly."""
        cache, mock_model, _ = cache_with_mocks

        embedding = cache._generate_embedding("test query")

        mock_model.encode.assert_called_once()
        assert len(embedding) == 384

    def test_compute_query_hash(self, cache_with_mocks):
        """Query hash should be deterministic and model-specific."""
        cache, _, _ = cache_with_mocks

        hash1 = cache._compute_query_hash("test query", "model-a")
        hash2 = cache._compute_query_hash("test query", "model-a")
        hash3 = cache._compute_query_hash("test query", "model-b")

        assert hash1 == hash2  # Same query, same model
        assert hash1 != hash3  # Same query, different model

    @pytest.mark.asyncio
    async def test_cache_miss_empty_results(self, cache_with_mocks):
        """Cache should return None when no similar queries found."""
        cache, _, mock_table = cache_with_mocks
        mock_table.to_list.return_value = []

        result = await cache.get("What is Python?", "gemini-2.5-flash")

        assert result is None
        assert cache._stats.cache_misses == 1

    @pytest.mark.asyncio
    async def test_cache_miss_low_similarity(self, cache_with_mocks):
        """Cache should return None when similarity is below threshold."""
        cache, _, mock_table = cache_with_mocks

        # Return a result with low similarity (high distance)
        mock_table.to_list.return_value = [
            {
                'cache_id': 'test-id',
                'query': 'What is Java?',
                'response': 'Java is a programming language.',
                'model_name': 'gemini-2.5-flash',
                'created_at': datetime.now().isoformat(),
                'hit_count': 0,
                '_distance': 0.5,  # Similarity = 0.5, below 0.92 threshold
            }
        ]

        result = await cache.get("What is Python?", "gemini-2.5-flash")

        assert result is None
        assert cache._stats.cache_misses == 1

    @pytest.mark.asyncio
    async def test_cache_hit(self, cache_with_mocks):
        """Cache should return entry when similarity exceeds threshold."""
        cache, _, mock_table = cache_with_mocks

        # Return a result with high similarity (low distance)
        mock_table.to_list.return_value = [
            {
                'cache_id': 'test-id',
                'query': 'What is Python?',
                'response': 'Python is a programming language.',
                'model_name': 'gemini-2.5-flash',
                'created_at': datetime.now().isoformat(),
                'hit_count': 5,
                '_distance': 0.05,  # Similarity = 0.95, above 0.92 threshold
            }
        ]

        result = await cache.get("What is Python?", "gemini-2.5-flash")

        assert result is not None
        assert isinstance(result, CacheEntry)
        assert result.response == 'Python is a programming language.'
        assert result.similarity_score == 0.95
        assert cache._stats.cache_hits == 1

    @pytest.mark.asyncio
    async def test_put_stores_entry(self, cache_with_mocks):
        """Put should store a new cache entry."""
        cache, _, mock_table = cache_with_mocks
        mock_table.to_list.return_value = []  # No existing entry

        success = await cache.put(
            query="What is Python?",
            response="Python is a programming language.",
            model_name="gemini-2.5-flash",
        )

        assert success is True
        mock_table.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_put_disabled_cache(self, cache_with_mocks):
        """Put should return False when cache is disabled."""
        cache, _, _ = cache_with_mocks
        cache.enabled = False

        success = await cache.put(
            query="test",
            response="test response",
            model_name="gemini-2.5-flash",
        )

        assert success is False

    def test_get_stats(self, cache_with_mocks):
        """Get stats should return current cache statistics."""
        cache, _, _ = cache_with_mocks
        cache._stats.total_queries = 100
        cache._stats.cache_hits = 35
        cache._stats.cache_misses = 65

        stats = cache.get_stats()

        assert stats['enabled'] is True
        assert stats['similarity_threshold'] == 0.92
        assert stats['total_queries'] == 100
        assert stats['cache_hits'] == 35
        assert stats['hit_rate_percent'] == 35.0

    @pytest.mark.asyncio
    async def test_clear_all(self, cache_with_mocks):
        """Clear should remove all cache entries."""
        cache, _, mock_table = cache_with_mocks

        # Mock pandas DataFrame with entries
        mock_df = MagicMock()
        mock_df.__len__ = lambda self: 10
        mock_table.to_pandas.return_value = mock_df

        count = await cache.clear()

        assert count == 10
        cache.db.drop_table.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_by_model(self, cache_with_mocks):
        """Clear should remove only entries for specified model."""
        cache, _, mock_table = cache_with_mocks

        # Reset the mock to clear calls from initialization
        mock_table.delete.reset_mock()

        # Mock pandas DataFrame with filtered entries
        import pandas as pd

        mock_df = pd.DataFrame(
            {
                'model_name': ['gemini-2.5-flash', 'gemini-2.5-flash', 'llama3.2'],
                'cache_id': ['id1', 'id2', 'id3'],
            }
        )
        mock_table.to_pandas.return_value = mock_df

        count = await cache.clear(model_name='gemini-2.5-flash')

        assert count == 2
        mock_table.delete.assert_called_once_with("model_name = 'gemini-2.5-flash'")


class TestSemanticCacheIntegration:
    """Integration-style tests with minimal mocking."""

    @pytest.mark.asyncio
    async def test_cache_flow_miss_then_hit(self):
        """Test the full cache flow: miss, store, then hit."""
        with patch(
            'src.app.services.semantic_cache.SENTENCE_TRANSFORMERS_AVAILABLE', True
        ), patch(
            'src.app.services.semantic_cache.LANCEDB_AVAILABLE', True
        ), patch(
            'src.app.services.semantic_cache.SentenceTransformer'
        ) as mock_st, patch(
            'src.app.services.semantic_cache.lancedb'
        ) as mock_lance:
            # Setup mocks
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.max_seq_length = 512
            mock_model.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)
            mock_st.return_value = mock_model

            mock_table = MagicMock()
            mock_table.to_pandas.return_value = MagicMock(__len__=lambda self: 0)

            # First call: no results (cache miss)
            # Second call: return stored result (cache hit)
            mock_table.search.return_value = mock_table
            mock_table.where.return_value = mock_table
            mock_table.limit.return_value = mock_table
            mock_table.to_list.side_effect = [
                [],  # First get: miss
                [],  # Put: check for existing
                [    # Second get: hit
                    {
                        'cache_id': 'test-id',
                        'query': 'What is Python?',
                        'response': 'Python is a programming language.',
                        'model_name': 'gemini-2.5-flash',
                        'created_at': datetime.now().isoformat(),
                        'hit_count': 0,
                        '_distance': 0.02,
                    }
                ],
            ]

            mock_db = MagicMock()
            mock_db.table_names.return_value = []
            mock_db.create_table.return_value = mock_table
            mock_lance.connect.return_value = mock_db

            # Create cache
            cache = SemanticCache(
                similarity_threshold=0.92,
                enabled=True,
                db_path='/tmp/test_cache',
            )
            cache.cache_table = mock_table
            cache.db = mock_db

            # First query: cache miss
            result1 = await cache.get("What is Python?", "gemini-2.5-flash")
            assert result1 is None
            assert cache._stats.cache_misses == 1

            # Store the response
            await cache.put(
                "What is Python?",
                "Python is a programming language.",
                "gemini-2.5-flash",
            )

            # Second query: cache hit
            result2 = await cache.get("What is Python?", "gemini-2.5-flash")
            assert result2 is not None
            assert result2.similarity_score == 0.98
            assert cache._stats.cache_hits == 1
