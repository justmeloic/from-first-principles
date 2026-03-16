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

"""Semantic similarity caching for LLM responses.

This module implements semantic caching to reduce latency and costs by storing
LLM responses and retrieving them for semantically similar queries. It uses
the same embedding model as the semantic search to ensure consistency.

Key Features:
- Reuses the embedding model from indexing pipeline
- Stores cache entries in LanceDB for persistent, efficient similarity search
- Configurable similarity threshold for cache hits
- Support for per-model caching to avoid cross-model contamination
- TTL support for cache expiration
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger as _logger

try:
    import lancedb

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


@dataclass
class CacheEntry:
    """Represents a cached query-response pair."""

    query: str
    response: str
    model_name: str
    similarity_score: float
    created_at: datetime
    hit_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class CacheStats:
    """Statistics about cache performance."""

    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_entries: int = 0
    avg_hit_latency_ms: float = 0.0
    avg_miss_latency_ms: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as a percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.cache_hits / self.total_queries) * 100


class SemanticCache:
    """Semantic similarity cache for LLM responses.

    This cache stores query-response pairs and retrieves cached responses
    for queries that are semantically similar to previously seen queries.

    The cache uses:
    - Same embedding model as semantic search (all-MiniLM-L6-v2 by default)
    - LanceDB for vector storage and similarity search
    - Cosine similarity for measuring query similarity
    """

    # Default configuration
    DEFAULT_SIMILARITY_THRESHOLD = 0.92  # High threshold for accuracy
    DEFAULT_CACHE_TABLE_NAME = 'semantic_cache'
    DEFAULT_MAX_CACHE_SIZE = 10000
    DEFAULT_TTL_HOURS = 24 * 7  # 1 week

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        cache_table_name: str = DEFAULT_CACHE_TABLE_NAME,
        max_cache_size: int = DEFAULT_MAX_CACHE_SIZE,
        ttl_hours: int = DEFAULT_TTL_HOURS,
        db_path: Optional[str] = None,
        model_name: str = 'all-MiniLM-L6-v2',
        enabled: bool = True,
    ):
        """Initialize the semantic cache.

        Args:
            similarity_threshold: Minimum similarity score for cache hit (0-1).
                Higher values require closer matches. Default 0.92.
            cache_table_name: Name of the LanceDB table for cache entries.
            max_cache_size: Maximum number of entries in the cache.
            ttl_hours: Time-to-live for cache entries in hours.
            db_path: Path to LanceDB database. Uses default if not specified.
            model_name: Name of the sentence transformer model to use.
            enabled: Whether caching is enabled.
        """
        self._logger = _logger
        self.enabled = enabled
        self.similarity_threshold = similarity_threshold
        self.cache_table_name = cache_table_name
        self.max_cache_size = max_cache_size
        self.ttl_hours = ttl_hours
        self.model_name = model_name

        # Initialize components
        self.embedding_model: Optional[SentenceTransformer] = None
        self.db: Optional[Any] = None
        self.cache_table: Optional[Any] = None
        self.embedding_dim: int = 0

        # Statistics
        self._stats = CacheStats()
        self._hit_latencies: List[float] = []
        self._miss_latencies: List[float] = []

        # Set up database path
        if db_path is None:
            # Use default path relative to the services/ai directory
            self.db_path = Path(__file__).parent.parent.parent.parent / 'data' / 'lancedb'
        else:
            self.db_path = Path(db_path)

        # Initialize if enabled
        if self.enabled:
            self._initialize()

    def _initialize(self) -> None:
        """Initialize the embedding model and database connection."""
        if not self.enabled:
            return

        try:
            self._initialize_embedding_model()
            self._initialize_database()
            self._logger.info(
                f'SemanticCache initialized: threshold={self.similarity_threshold}, '
                f'model={self.model_name}, db={self.db_path}'
            )
        except Exception as e:
            self._logger.error(f'Failed to initialize SemanticCache: {e}')
            self.enabled = False

    def _initialize_embedding_model(self) -> None:
        """Initialize the sentence transformer embedding model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                'sentence-transformers is required for semantic caching. '
                'Install with: pip install sentence-transformers'
            )

        self._logger.info(f'Loading embedding model: {self.model_name}')
        self.embedding_model = SentenceTransformer(self.model_name, device='cpu')
        dim = self.embedding_model.get_sentence_embedding_dimension()
        if dim is None:
            raise RuntimeError('Could not determine embedding dimension')
        self.embedding_dim = dim
        self._logger.info(
            f'Embedding model loaded: dim={self.embedding_dim}, '
            f'max_seq_len={self.embedding_model.max_seq_length}'
        )

    def _initialize_database(self) -> None:
        """Initialize LanceDB connection and cache table."""
        if not LANCEDB_AVAILABLE:
            raise ImportError(
                'lancedb is required for semantic caching. '
                'Install with: pip install lancedb'
            )

        # Ensure database directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Connect to database
        self.db = lancedb.connect(str(self.db_path))
        self._logger.info(f'Connected to LanceDB at: {self.db_path}')

        # Initialize cache table
        self._ensure_cache_table_exists()

    def _ensure_cache_table_exists(self) -> None:
        """Ensure the cache table exists with correct schema."""
        if self.db is None:
            return

        try:
            table_names = self.db.table_names()

            if self.cache_table_name not in table_names:
                self._create_cache_table()
            else:
                self.cache_table = self.db.open_table(self.cache_table_name)
                self._logger.info(f'Opened existing cache table: {self.cache_table_name}')

        except Exception as e:
            self._logger.error(f'Error setting up cache table: {e}')
            self._create_cache_table()

    def _create_cache_table(self) -> None:
        """Create the cache table with the correct schema."""
        if self.db is None:
            raise RuntimeError('Database not initialized')

        self._logger.info(f'Creating cache table: {self.cache_table_name}')

        # Create sample entry to establish schema
        sample_entry = {
            'cache_id': 'sample_entry_for_schema',
            'query': 'Sample query for schema creation',
            'query_hash': hashlib.md5('sample'.encode()).hexdigest(),
            'response': 'Sample response',
            'model_name': self.model_name,
            'vector': [0.0] * self.embedding_dim,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'hit_count': 0,
            'ttl_hours': self.ttl_hours,
        }

        # Create table
        self.cache_table = self.db.create_table(self.cache_table_name, [sample_entry])

        # Remove sample entry
        if self.cache_table is not None:
            self.cache_table.delete("cache_id = 'sample_entry_for_schema'")
        self._logger.info(f'Created cache table: {self.cache_table_name}')

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text.

        Args:
            text: The text to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        if self.embedding_model is None:
            raise RuntimeError('Embedding model not initialized')

        # Normalize and encode
        embedding = self.embedding_model.encode(
            text.strip(),
            convert_to_tensor=False,
            normalize_embeddings=True,
        )

        # Convert to list of floats
        if hasattr(embedding, 'tolist'):
            result = embedding.tolist()
        else:
            result = [float(x) for x in embedding]
        return result  # type: ignore[return-value]

    def _compute_query_hash(self, query: str, model_name: str) -> str:
        """Compute a hash for exact query matching.

        Args:
            query: The query text.
            model_name: The model name (for model-specific caching).

        Returns:
            MD5 hash of the normalized query and model.
        """
        normalized = f'{model_name}:{query.strip().lower()}'
        return hashlib.md5(normalized.encode()).hexdigest()

    async def get(
        self,
        query: str,
        model_name: str,
    ) -> Optional[CacheEntry]:
        """Look up a cached response for a semantically similar query.

        This method:
        1. Generates an embedding for the query
        2. Searches for similar queries in the cache
        3. Returns the cached response if similarity exceeds threshold

        Args:
            query: The user's query text.
            model_name: The model name to ensure model-specific caching.

        Returns:
            CacheEntry if a cache hit is found, None otherwise.
        """
        if not self.enabled or self.cache_table is None:
            return None

        start_time = time.time()
        self._stats.total_queries += 1

        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Search for similar queries in cache
            # Filter by model name to avoid cross-model contamination
            results = (
                self.cache_table.search(query_embedding)
                .where(f"model_name = '{model_name}'")
                .limit(1)
                .to_list()
            )

            if not results:
                self._record_miss(start_time)
                return None

            result = results[0]

            # Calculate similarity score (LanceDB returns distance, not similarity)
            # For normalized vectors with cosine distance: similarity = 1 - distance
            distance = result.get('_distance', 1.0)
            similarity_score = 1.0 - distance

            # Check if similarity exceeds threshold
            if similarity_score < self.similarity_threshold:
                self._logger.debug(
                    f'Cache miss: similarity {similarity_score:.4f} < '
                    f'threshold {self.similarity_threshold}'
                )
                self._record_miss(start_time)
                return None

            # Cache hit!
            self._record_hit(start_time)

            # Update access statistics (fire and forget)
            await self._update_access_stats(result['cache_id'])

            self._logger.info(
                f'Cache hit: similarity={similarity_score:.4f}, '
                f'query="{query[:50]}..."'
            )

            return CacheEntry(
                query=result['query'],
                response=result['response'],
                model_name=result['model_name'],
                similarity_score=similarity_score,
                created_at=datetime.fromisoformat(result['created_at']),
                hit_count=result.get('hit_count', 0) + 1,
                last_accessed=datetime.now(),
            )

        except Exception as e:
            self._logger.error(f'Error during cache lookup: {e}')
            self._record_miss(start_time)
            return None

    async def put(
        self,
        query: str,
        response: str,
        model_name: str,
    ) -> bool:
        """Store a query-response pair in the cache.

        Args:
            query: The original user query.
            response: The LLM-generated response.
            model_name: The model that generated the response.

        Returns:
            True if successfully cached, False otherwise.
        """
        if not self.enabled or self.cache_table is None:
            return False

        try:
            # Check cache size and evict if necessary
            await self._evict_if_needed()

            # Generate embedding for the query
            query_embedding = self._generate_embedding(query)
            query_hash = self._compute_query_hash(query, model_name)

            # Check for existing exact match (avoid duplicates)
            existing = (
                self.cache_table.search(query_embedding)
                .where(f"query_hash = '{query_hash}'")
                .limit(1)
                .to_list()
            )

            if existing:
                # Update existing entry
                self._logger.debug(f'Updating existing cache entry: {query_hash}')
                self.cache_table.delete(f"query_hash = '{query_hash}'")

            # Create new cache entry
            cache_entry = {
                'cache_id': str(uuid.uuid4()),
                'query': query,
                'query_hash': query_hash,
                'response': response,
                'model_name': model_name,
                'vector': query_embedding,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'hit_count': 0,
                'ttl_hours': self.ttl_hours,
            }

            # Insert into cache
            self.cache_table.add([cache_entry])
            self._stats.total_entries = len(self.cache_table.to_pandas())

            self._logger.debug(
                f'Cached response for query: "{query[:50]}..." '
                f'(model: {model_name})'
            )
            return True

        except Exception as e:
            self._logger.error(f'Error caching response: {e}')
            return False

    async def _update_access_stats(self, cache_id: str) -> None:
        """Update access statistics for a cache entry.

        Args:
            cache_id: The ID of the cache entry to update.
        """
        try:
            # LanceDB doesn't support direct updates easily,
            # so we'll just log for now. For production, consider
            # using a separate stats table or updating periodically.
            pass
        except Exception as e:
            self._logger.debug(f'Failed to update access stats: {e}')

    async def _evict_if_needed(self) -> None:
        """Evict old entries if cache size exceeds maximum."""
        if self.cache_table is None:
            return

        try:
            current_size = len(self.cache_table.to_pandas())

            if current_size >= self.max_cache_size:
                # Evict oldest 10% of entries
                evict_count = int(self.max_cache_size * 0.1)
                self._logger.info(
                    f'Cache size {current_size} >= max {self.max_cache_size}, '
                    f'evicting {evict_count} oldest entries'
                )

                # Get oldest entries
                df = self.cache_table.to_pandas()
                df_sorted = df.sort_values('created_at', ascending=True)
                ids_to_evict = df_sorted['cache_id'].head(evict_count).tolist()

                # Delete oldest entries
                for cache_id in ids_to_evict:
                    self.cache_table.delete(f"cache_id = '{cache_id}'")

                self._logger.info(f'Evicted {len(ids_to_evict)} cache entries')

            # Also evict expired entries (TTL)
            await self._evict_expired()

        except Exception as e:
            self._logger.error(f'Error during cache eviction: {e}')

    async def _evict_expired(self) -> None:
        """Evict entries that have exceeded their TTL."""
        if self.cache_table is None:
            return

        try:
            df = self.cache_table.to_pandas()
            if df.empty:
                return

            now = datetime.now()
            expired_ids = []

            for _, row in df.iterrows():
                created = datetime.fromisoformat(row['created_at'])
                ttl = row.get('ttl_hours', self.ttl_hours)
                age_hours = (now - created).total_seconds() / 3600

                if age_hours > ttl:
                    expired_ids.append(row['cache_id'])

            if expired_ids:
                for cache_id in expired_ids:
                    self.cache_table.delete(f"cache_id = '{cache_id}'")
                self._logger.info(f'Evicted {len(expired_ids)} expired cache entries')

        except Exception as e:
            self._logger.debug(f'Error evicting expired entries: {e}')

    def _record_hit(self, start_time: float) -> None:
        """Record a cache hit for statistics."""
        latency = (time.time() - start_time) * 1000
        self._stats.cache_hits += 1
        self._hit_latencies.append(latency)

        # Keep only last 1000 latencies
        if len(self._hit_latencies) > 1000:
            self._hit_latencies = self._hit_latencies[-1000:]

        self._stats.avg_hit_latency_ms = (
            sum(self._hit_latencies) / len(self._hit_latencies)
        )

    def _record_miss(self, start_time: float) -> None:
        """Record a cache miss for statistics."""
        latency = (time.time() - start_time) * 1000
        self._stats.cache_misses += 1
        self._miss_latencies.append(latency)

        # Keep only last 1000 latencies
        if len(self._miss_latencies) > 1000:
            self._miss_latencies = self._miss_latencies[-1000:]

        self._stats.avg_miss_latency_ms = (
            sum(self._miss_latencies) / len(self._miss_latencies)
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics.
        """
        return {
            'enabled': self.enabled,
            'similarity_threshold': self.similarity_threshold,
            'total_queries': self._stats.total_queries,
            'cache_hits': self._stats.cache_hits,
            'cache_misses': self._stats.cache_misses,
            'hit_rate_percent': round(self._stats.hit_rate, 2),
            'total_entries': self._stats.total_entries,
            'max_cache_size': self.max_cache_size,
            'avg_hit_latency_ms': round(self._stats.avg_hit_latency_ms, 2),
            'avg_miss_latency_ms': round(self._stats.avg_miss_latency_ms, 2),
            'model_name': self.model_name,
            'ttl_hours': self.ttl_hours,
        }

    async def clear(self, model_name: Optional[str] = None) -> int:
        """Clear the cache.

        Args:
            model_name: If specified, only clear entries for this model.
                       Otherwise, clear all entries.

        Returns:
            Number of entries cleared.
        """
        if self.cache_table is None or self.db is None:
            return 0

        try:
            if model_name:
                # Clear only entries for specific model
                df = self.cache_table.to_pandas()
                count = len(df[df['model_name'] == model_name])
                self.cache_table.delete(f"model_name = '{model_name}'")
            else:
                # Clear all entries
                count = len(self.cache_table.to_pandas())
                self.db.drop_table(self.cache_table_name)
                self._create_cache_table()

            if self.cache_table is not None:
                self._stats.total_entries = len(self.cache_table.to_pandas())
            self._logger.info(f'Cleared {count} cache entries')
            return count

        except Exception as e:
            self._logger.error(f'Error clearing cache: {e}')
            return 0

    async def invalidate_similar(
        self,
        query: str,
        threshold: float = 0.95,
    ) -> int:
        """Invalidate cache entries similar to the given query.

        Useful for invalidating cached responses when the underlying
        data or model behavior has changed.

        Args:
            query: Query to find similar entries for.
            threshold: Similarity threshold for invalidation.

        Returns:
            Number of entries invalidated.
        """
        if self.cache_table is None:
            return 0

        try:
            query_embedding = self._generate_embedding(query)
            results = (
                self.cache_table.search(query_embedding)
                .limit(100)
                .to_list()
            )

            invalidated = 0
            for result in results:
                distance = result.get('_distance', 1.0)
                similarity = 1.0 - distance

                if similarity >= threshold:
                    self.cache_table.delete(f"cache_id = '{result['cache_id']}'")
                    invalidated += 1

            if invalidated:
                self._logger.info(
                    f'Invalidated {invalidated} cache entries similar to: '
                    f'"{query[:50]}..."'
                )

            return invalidated

        except Exception as e:
            self._logger.error(f'Error invalidating cache entries: {e}')
            return 0


# Global semantic cache instance (initialized lazily)
_semantic_cache: Optional[SemanticCache] = None


def get_semantic_cache() -> SemanticCache:
    """Get or create the global semantic cache instance.

    Returns:
        The global SemanticCache instance.
    """
    global _semantic_cache

    if _semantic_cache is None:
        # Import settings here to avoid circular imports
        try:
            from src.app.core.config import settings

            _semantic_cache = SemanticCache(
                similarity_threshold=getattr(
                    settings, 'CACHE_SIMILARITY_THRESHOLD', 0.92
                ),
                enabled=getattr(settings, 'CACHE_ENABLED', True),
                ttl_hours=getattr(settings, 'CACHE_TTL_HOURS', 24 * 7),
                max_cache_size=getattr(settings, 'CACHE_MAX_SIZE', 10000),
            )
        except Exception as e:
            _logger.warning(
                f'Failed to initialize semantic cache with settings: {e}. '
                'Using defaults.'
            )
            _semantic_cache = SemanticCache()

    return _semantic_cache
