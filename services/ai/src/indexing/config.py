"""
Configuration management for the blog indexing pipeline.

This module provides centralized configuration with Pydantic validation
and environment-specific settings optimized for local deployment.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class EmbeddingConfig(BaseModel):
    """Configuration for text embedding generation."""

    # Model selection based on device capabilities
    model_name: str = Field(
        default='all-MiniLM-L6-v2',
        description='Sentence transformer model name. Lightweight default for Raspberry Pi.',
    )

    # Alternative models for different use cases
    high_quality_model: str = Field(
        default='all-mpnet-base-v2',
        description='Higher quality model for better accuracy (more resources required).',
    )

    multilingual_model: str = Field(
        default='paraphrase-multilingual-MiniLM-L12-v2',
        description='Model for multilingual content support.',
    )

    # Processing parameters
    batch_size: int = Field(
        default=16,
        description='Batch size for embedding generation. Adjust based on available memory.',
    )

    device: str = Field(
        default='cpu',
        description="Device to use for inference: 'cpu', 'cuda', or 'mps'.",
    )

    max_sequence_length: int = Field(
        default=512, description='Maximum sequence length for the model.'
    )


class ChunkingConfig(BaseModel):
    """Configuration for text chunking strategy."""

    chunk_size: int = Field(
        default=1000, description='Target size for text chunks in characters.'
    )

    chunk_overlap: int = Field(
        default=200, description='Overlap between chunks to maintain context.'
    )

    min_chunk_size: int = Field(
        default=100, description='Minimum chunk size to avoid tiny fragments.'
    )

    # Splitting strategy
    preserve_paragraphs: bool = Field(
        default=True, description='Try to keep paragraphs intact when possible.'
    )

    preserve_sections: bool = Field(
        default=True, description='Try to keep sections intact when possible.'
    )


class DatabaseConfig(BaseModel):
    """Configuration for LanceDB database."""

    db_path: str = Field(
        default='./data/lancedb', description='Path to the LanceDB database directory.'
    )

    table_name: str = Field(
        default='blog_content', description='Name of the main content table.'
    )

    metadata_table_name: str = Field(
        default='content_metadata', description='Name of the metadata table.'
    )

    # Index configuration
    create_ivf_index: bool = Field(
        default=True, description='Create IVF index for faster vector search.'
    )

    ivf_partitions: int = Field(
        default=256, description='Number of partitions for IVF index.'
    )


class ContentConfig(BaseModel):
    """Configuration for content processing."""

    content_root: str = Field(
        default='./data/content', description='Root directory containing blog content.'
    )

    supported_categories: List[str] = Field(
        default=['blog', 'engineering'], description='Supported content categories.'
    )

    markdown_file: str = Field(
        default='body.md',
        description='Name of the main markdown file in each post directory.',
    )

    metadata_file: str = Field(
        default='metadata.yaml',
        description='Name of the metadata file in each post directory.',
    )

    # Content filtering
    include_drafts: bool = Field(
        default=False, description='Whether to include draft posts in indexing.'
    )

    min_content_length: int = Field(
        default=100, description='Minimum content length to be included in index.'
    )


class ProcessingConfig(BaseModel):
    """Configuration for processing behavior."""

    # Memory management
    max_memory_usage_mb: int = Field(
        default=512,
        description='Maximum memory usage in MB (important for Raspberry Pi).',
    )

    # Concurrency
    max_workers: int = Field(default=2, description='Maximum number of worker threads.')

    # Caching
    enable_embedding_cache: bool = Field(
        default=True, description='Cache embeddings to avoid recomputation.'
    )

    cache_dir: str = Field(
        default='./data/cache',
        description='Directory for caching embeddings and processed content.',
    )

    # Change detection
    check_content_hash: bool = Field(
        default=True, description='Check content hash for change detection.'
    )


class IndexingConfig(BaseSettings):
    """Main configuration class for the indexing pipeline."""

    # Sub-configurations
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    content: ContentConfig = Field(default_factory=ContentConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)

    # Global settings
    log_level: str = Field(
        default='INFO', description='Logging level: DEBUG, INFO, WARNING, ERROR.'
    )

    # Environment detection
    environment: str = Field(
        default='development', description='Environment: development, production.'
    )

    # Auto-detect device capabilities
    auto_detect_device: bool = Field(
        default=True,
        description='Automatically detect best device (CPU/GPU) and adjust settings.',
    )

    class Config:
        env_prefix = 'INDEXING_'
        case_sensitive = False
        env_file = '.env.indexing'
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra fields from .env file

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Auto-detect and optimize settings
        if self.auto_detect_device:
            self._optimize_for_device()

        # Ensure paths are absolute
        self._resolve_paths()

    def _optimize_for_device(self):
        """Automatically optimize settings based on detected hardware."""
        import psutil
        import torch

        # Get available memory
        available_memory_gb = psutil.virtual_memory().available / (1024**3)

        # Adjust settings based on available memory
        if available_memory_gb < 2:  # Raspberry Pi or low-memory device
            self.embedding.batch_size = 8
            self.processing.max_memory_usage_mb = 256
            self.processing.max_workers = 1
            self.database.ivf_partitions = 64
        elif available_memory_gb < 4:
            self.embedding.batch_size = 16
            self.processing.max_memory_usage_mb = 512
            self.processing.max_workers = 2
        else:
            self.embedding.batch_size = 32
            self.processing.max_memory_usage_mb = 1024
            self.processing.max_workers = 4

        # Detect best device for embeddings with colored output
        if torch.cuda.is_available():
            self.embedding.device = 'cuda'
            print(
                '\033[92m🚀 GPU Accelerator detected! '
                'Loading embeddings to CUDA device\033[0m'
            )
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.embedding.device = 'mps'
            print(
                '\033[92m🚀 MPS Accelerator detected! '
                'Loading embeddings to Apple Silicon GPU\033[0m'
            )
        else:
            self.embedding.device = 'cpu'
            print(
                '\033[93m⚠️  No GPU accelerator found, using CPU for embeddings\033[0m'
            )
            print(
                '\033[91m💀 WARNING: If running on Raspberry Pi, CPU-only embedding '
                'generation may cause system instability,\n'
                '    overheating, or hardware failure! - Loïc :( \033[0m'
            )

    def _resolve_paths(self):
        """Convert relative paths to absolute paths."""
        # Only resolve paths if they are still relative (not overridden by env vars)
        if not os.path.isabs(self.content.content_root):
            self.content.content_root = os.path.abspath(self.content.content_root)

        if not os.path.isabs(self.database.db_path):
            self.database.db_path = os.path.abspath(self.database.db_path)

        if not os.path.isabs(self.processing.cache_dir):
            self.processing.cache_dir = os.path.abspath(self.processing.cache_dir)

    @classmethod
    def for_raspberry_pi(cls) -> 'IndexingConfig':
        """Create configuration optimized for Raspberry Pi deployment."""
        return cls(
            embedding=EmbeddingConfig(
                model_name='all-MiniLM-L6-v2', batch_size=8, device='cpu'
            ),
            processing=ProcessingConfig(max_memory_usage_mb=256, max_workers=1),
            database=DatabaseConfig(ivf_partitions=64),
            auto_detect_device=False,
        )

    @classmethod
    def for_development(cls) -> 'IndexingConfig':
        """Create configuration optimized for development."""
        return cls(
            embedding=EmbeddingConfig(
                batch_size=4,  # Small batches for quick testing
            ),
            content=ContentConfig(
                include_drafts=True  # Include drafts during development
            ),
            log_level='DEBUG',
        )


# Global configuration instance
_config = None


def get_config() -> IndexingConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = IndexingConfig()
    return _config


def reload_config(**overrides) -> IndexingConfig:
    """Reload configuration with optional overrides."""
    global _config
    _config = IndexingConfig(**overrides)
    return _config
