"""
Blog content indexing pipeline.

This package provides a complete solution for indexing blog content,
generating embeddings, and enabling semantic search capabilities.

Key components:
- Content loading and parsing from filesystem
- Text processing and intelligent chunking
- Vector embedding generation using sentence transformers
- LanceDB storage for efficient vector search
- Configuration management optimized for local deployment

Usage:
    from indexing import IndexingPipeline

    pipeline = IndexingPipeline()
    result = pipeline.index_all_posts()
    print(f"Indexed {result.posts_processed} posts")
"""

from .builder import IndexingPipeline
from .config import IndexingConfig, get_config, reload_config
from .document import (
    BlogPost,
    ContentChunk,
    ContentMetadata,
    EmbeddingVector,
    IndexingResult,
    SearchQuery,
    SearchResponse,
    SearchResult,
)
from .embedder import EmbeddingGenerator
from .loader import ContentLoader
from .utils.text_processing import TextProcessor

__version__ = '0.1.0'

__all__ = [
    # Main pipeline
    'IndexingPipeline',
    # Configuration
    'IndexingConfig',
    'get_config',
    'reload_config',
    # Core components
    'ContentLoader',
    'EmbeddingGenerator',
    'TextProcessor',
    # Data models
    'BlogPost',
    'ContentChunk',
    'ContentMetadata',
    'EmbeddingVector',
    'IndexingResult',
    'SearchQuery',
    'SearchResult',
    'SearchResponse',
]


def create_pipeline(config=None, **config_overrides):
    """
    Create and configure an indexing pipeline.

    Args:
        config: Optional IndexingConfig instance
        **config_overrides: Override specific configuration values

    Returns:
        IndexingPipeline: Configured pipeline ready for use

    Example:
        # Use default configuration
        pipeline = create_pipeline()

        # Override specific settings
        pipeline = create_pipeline(
            embedding__model_name="all-mpnet-base-v2",
            chunking__chunk_size=1500
        )

        # Use Raspberry Pi optimized settings
        pipeline = create_pipeline(config=IndexingConfig.for_raspberry_pi())
    """
    if config is None:
        if config_overrides:
            config = reload_config(**config_overrides)
        else:
            config = get_config()

    return IndexingPipeline(config)


def quick_test():
    """
    Quick test of the indexing pipeline.

    Returns:
        dict: Test results
    """
    try:
        pipeline = create_pipeline()
        return pipeline.test_pipeline()
    except Exception as e:
        return {'success': False, 'error': f'Pipeline test failed: {e}'}


# Convenience functions for common operations
def index_all_content(force_reindex=False, **config_overrides):
    """
    Index all blog content with optional configuration overrides.

    Args:
        force_reindex: Whether to reindex all content regardless of changes
        **config_overrides: Configuration overrides

    Returns:
        IndexingResult: Results of the indexing operation
    """
    pipeline = create_pipeline(**config_overrides)
    return pipeline.index_all_posts(force_reindex=force_reindex)


def index_single_post(category, slug, **config_overrides):
    """
    Index a single blog post.

    Args:
        category: Post category (blog/engineering)
        slug: Post slug
        **config_overrides: Configuration overrides

    Returns:
        IndexingResult: Results of the indexing operation
    """
    pipeline = create_pipeline(**config_overrides)
    return pipeline.index_single_post(category, slug)


def get_indexing_stats(**config_overrides):
    """
    Get statistics about indexed content.

    Args:
        **config_overrides: Configuration overrides

    Returns:
        dict: Indexing statistics
    """
    pipeline = create_pipeline(**config_overrides)
    return pipeline.get_indexing_stats()
