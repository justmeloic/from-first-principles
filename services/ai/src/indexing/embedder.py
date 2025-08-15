"""
Embedding generator for the blog indexing pipeline.

This module handles generating vector embeddings for text content using
sentence transformers optimized for local deployment.
"""

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import torch
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .config import get_config
from .document import ContentChunk, EmbeddingVector


class EmbeddingGenerator:
    """Generate vector embeddings for text content."""

    def __init__(self, config=None):
        """Initialize the embedding generator."""
        self.config = config or get_config()
        self.model = None
        self.model_info = {}
        self._embedding_cache = {}

        # Initialize the model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                'sentence-transformers is required for embedding generation. '
                'Install with: pip install sentence-transformers'
            )

        try:
            # Load the model
            model_name = self.config.embedding.model_name
            device = self.config.embedding.device

            print(f'Loading embedding model: {model_name} on {device}')

            self.model = SentenceTransformer(model_name, device=device)

            # Store model information
            self.model_info = {
                'name': model_name,
                'device': device,
                'max_seq_length': self.model.max_seq_length,
                'embedding_dimension': self.model.get_sentence_embedding_dimension(),
            }

            print(f'Model loaded successfully:')
            print(f'  - Max sequence length: {self.model_info["max_seq_length"]}')
            print(f'  - Embedding dimension: {self.model_info["embedding_dimension"]}')

        except Exception as e:
            raise RuntimeError(f'Failed to initialize embedding model: {e}')

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        model_key = (
            f'{self.model_info["name"]}_{self.model_info["embedding_dimension"]}'
        )
        return f'{model_key}_{text_hash}'

    def _check_cache(self, text: str) -> Optional[List[float]]:
        """Check if embedding exists in cache."""
        if not self.config.processing.enable_embedding_cache:
            return None

        cache_key = self._get_cache_key(text)
        return self._embedding_cache.get(cache_key)

    def _store_cache(self, text: str, embedding: List[float]):
        """Store embedding in cache."""
        if not self.config.processing.enable_embedding_cache:
            return

        cache_key = self._get_cache_key(text)
        self._embedding_cache[cache_key] = embedding

    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit model's maximum sequence length."""
        max_length = self.config.embedding.max_sequence_length

        # Simple truncation - could be improved with tokenizer
        if len(text) > max_length:
            # Try to truncate at sentence boundary
            truncated = text[:max_length]
            last_period = truncated.rfind('.')

            if last_period > max_length * 0.8:  # Keep if we don't lose too much
                return truncated[: last_period + 1]
            else:
                return truncated

        return text

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            raise ValueError('Text cannot be empty')

        # Check cache first
        cached_embedding = self._check_cache(text)
        if cached_embedding is not None:
            return cached_embedding

        # Truncate text if necessary
        processed_text = self._truncate_text(text.strip())

        try:
            # Generate embedding
            embedding = self.model.encode(
                processed_text, convert_to_tensor=False, normalize_embeddings=True
            )

            # Convert to list
            if hasattr(embedding, 'tolist'):
                embedding_list = embedding.tolist()
            else:
                embedding_list = list(embedding)

            # Store in cache
            self._store_cache(text, embedding_list)

            return embedding_list

        except Exception as e:
            raise RuntimeError(f'Failed to generate embedding: {e}')

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch."""
        if not texts:
            return []

        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        cached_embeddings = {}

        for i, text in enumerate(texts):
            if not text or not text.strip():
                continue

            # Check cache
            cached = self._check_cache(text)
            if cached is not None:
                cached_embeddings[i] = cached
            else:
                valid_texts.append(self._truncate_text(text.strip()))
                valid_indices.append(i)

        # Generate embeddings for non-cached texts
        new_embeddings = []
        if valid_texts:
            try:
                batch_size = self.config.embedding.batch_size

                # Process in batches
                for i in range(0, len(valid_texts), batch_size):
                    batch = valid_texts[i : i + batch_size]

                    batch_embeddings = self.model.encode(
                        batch,
                        convert_to_tensor=False,
                        normalize_embeddings=True,
                        batch_size=len(batch),
                    )

                    # Convert to lists and cache
                    for j, embedding in enumerate(batch_embeddings):
                        if hasattr(embedding, 'tolist'):
                            embedding_list = embedding.tolist()
                        else:
                            embedding_list = list(embedding)

                        new_embeddings.append(embedding_list)

                        # Store in cache
                        original_text = texts[valid_indices[i + j]]
                        self._store_cache(original_text, embedding_list)

            except Exception as e:
                raise RuntimeError(f'Failed to generate batch embeddings: {e}')

        # Combine cached and new embeddings in correct order
        result = [None] * len(texts)

        # Add cached embeddings
        for i, embedding in cached_embeddings.items():
            result[i] = embedding

        # Add new embeddings
        new_embedding_idx = 0
        for i in valid_indices:
            if result[i] is None:  # Not cached
                result[i] = new_embeddings[new_embedding_idx]
                new_embedding_idx += 1

        # Filter out None values (empty texts)
        return [emb for emb in result if emb is not None]

    def create_embedding_vectors(
        self, chunks: List[ContentChunk]
    ) -> List[EmbeddingVector]:
        """Create embedding vectors for content chunks."""
        if not chunks:
            return []

        # Extract texts and measure processing time
        start_time = time.time()
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings in batch
        embeddings = self.generate_embeddings_batch(texts)

        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        avg_time_per_chunk = processing_time / len(chunks) if chunks else 0

        # Create EmbeddingVector objects
        embedding_vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector = EmbeddingVector(
                chunk_id=chunk.chunk_id,
                vector=embedding,
                vector_dim=len(embedding),
                model_name=self.model_info['name'],
                model_version=None,  # Could be added if available
                processing_time_ms=avg_time_per_chunk,
            )
            embedding_vectors.append(vector)

        print(
            f'Generated {len(embedding_vectors)} embeddings in {processing_time:.2f}ms'
        )
        print(f'Average time per embedding: {avg_time_per_chunk:.2f}ms')

        return embedding_vectors

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return self.model_info.copy()

    def clear_cache(self):
        """Clear the embedding cache."""
        self._embedding_cache.clear()
        print('Embedding cache cleared')

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding cache."""
        return {
            'cache_size': len(self._embedding_cache),
            'cache_enabled': self.config.processing.enable_embedding_cache,
        }

    def save_cache(self, cache_file: Optional[Path] = None):
        """Save embedding cache to disk."""
        if not self.config.processing.enable_embedding_cache:
            return

        if cache_file is None:
            cache_dir = Path(self.config.processing.cache_dir)
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / 'embedding_cache.json'

        try:
            import json

            with open(cache_file, 'w') as f:
                json.dump(self._embedding_cache, f)

            print(f'Saved embedding cache to {cache_file}')

        except Exception as e:
            print(f'Failed to save cache: {e}')

    def load_cache(self, cache_file: Optional[Path] = None):
        """Load embedding cache from disk."""
        if not self.config.processing.enable_embedding_cache:
            return

        if cache_file is None:
            cache_dir = Path(self.config.processing.cache_dir)
            cache_file = cache_dir / 'embedding_cache.json'

        if not cache_file.exists():
            return

        try:
            import json

            with open(cache_file, 'r') as f:
                self._embedding_cache = json.load(f)

            print(f'Loaded embedding cache from {cache_file}')
            print(f'Cache contains {len(self._embedding_cache)} embeddings')

        except Exception as e:
            print(f'Failed to load cache: {e}')

    def test_embedding(
        self, test_text: str = 'This is a test sentence.'
    ) -> Dict[str, Any]:
        """Test the embedding generation with a sample text."""
        try:
            start_time = time.time()
            embedding = self.generate_embedding(test_text)
            processing_time = (time.time() - start_time) * 1000

            return {
                'success': True,
                'text_length': len(test_text),
                'embedding_dimension': len(embedding),
                'processing_time_ms': processing_time,
                'model_info': self.model_info,
                'sample_embedding': embedding[:5],  # First 5 dimensions
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'model_info': self.model_info}
