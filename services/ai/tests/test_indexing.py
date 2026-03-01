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
Tests for the indexing pipeline.

This module verifies that the indexing pipeline components can be imported
and instantiated correctly, and that configuration defaults are valid.
"""

import typer

from src.indexing import (
    BlogPost,
    ContentChunk,
    ContentMetadata,
    EmbeddingGenerator,
    EmbeddingVector,
    IndexingConfig,
    IndexingPipeline,
    IndexingResult,
    SearchQuery,
    SearchResponse,
    SearchResult,
    TextProcessor,
    get_config,
)
from src.indexing.main import app


class TestIndexingImports:
    """Verify that all indexing pipeline modules are importable."""

    def test_cli_app_is_typer_instance(self):
        """The CLI entry point should be a Typer application."""
        assert isinstance(app, typer.Typer)

    def test_pipeline_class_importable(self):
        """The IndexingPipeline class should be importable."""
        assert IndexingPipeline is not None

    def test_document_models_importable(self):
        """All document model classes should be importable."""
        assert BlogPost is not None
        assert ContentChunk is not None
        assert ContentMetadata is not None
        assert EmbeddingVector is not None
        assert IndexingResult is not None
        assert SearchQuery is not None
        assert SearchResponse is not None
        assert SearchResult is not None

    def test_embedding_generator_importable(self):
        """The EmbeddingGenerator class should be importable."""
        assert EmbeddingGenerator is not None

    def test_text_processor_importable(self):
        """The TextProcessor utility should be importable."""
        assert TextProcessor is not None


class TestIndexingConfig:
    """Verify indexing configuration defaults."""

    def test_default_config_loads(self):
        """The default configuration should load without errors."""
        config = get_config()
        assert isinstance(config, IndexingConfig)

    def test_default_embedding_model(self):
        """The default embedding model should be set."""
        config = get_config()
        assert config.embedding.model_name == 'all-MiniLM-L6-v2'

    def test_default_embedding_device(self):
        """The default embedding device should be a valid compute target."""
        config = get_config()
        assert config.embedding.device in ('cpu', 'cuda', 'mps')

    def test_supported_categories(self):
        """The configuration should define supported content categories."""
        config = get_config()
        assert len(config.content.supported_categories) > 0
