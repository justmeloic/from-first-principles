"""
Document models and schemas for the blog indexing pipeline.

This module defines Pydantic models for content, metadata, and embeddings
with comprehensive validation and type safety.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, computed_field, validator


class ContentMetadata(BaseModel):
    """Rich metadata for blog posts with validation."""

    # Core metadata
    title: str = Field(..., description='Full article title')
    slug: str = Field(..., description='URL-friendly identifier')
    author: str = Field(..., description='Author name')
    author_url: Optional[str] = Field(None, description='Author profile URL')
    publish_date: str = Field(..., description='Publication date (YYYY-MM-DD)')
    last_modified: str = Field(..., description='Last modification date')
    category: str = Field(..., description='Content category (blog/engineering)')
    tags: List[str] = Field(default_factory=list, description='Content tags')
    description: str = Field(..., description='Short description')
    excerpt: str = Field(..., description='Brief excerpt from content')
    reading_time: int = Field(..., description='Estimated reading time in minutes')
    word_count: int = Field(..., description='Approximate word count')
    featured: bool = Field(default=False, description='Whether post is featured')
    status: str = Field(default='published', description='Publication status')

    # SEO metadata
    seo: Dict[str, Any] = Field(default_factory=dict, description='SEO metadata')

    # Social media metadata
    social: Dict[str, Any] = Field(
        default_factory=dict, description='Social media metadata'
    )

    # Content structure
    content: Dict[str, Any] = Field(
        default_factory=dict, description='Content structure info'
    )

    # Technical metadata (auto-generated)
    technical: Dict[str, Any] = Field(
        default_factory=dict, description='Technical metadata'
    )

    @validator('category')
    def validate_category(cls, v):
        """Validate category is one of the supported types."""
        allowed_categories = ['blog', 'engineering']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of {allowed_categories}')
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate status is one of the allowed values."""
        allowed_statuses = ['draft', 'published', 'archived']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    @computed_field
    @property
    def canonical_url(self) -> str:
        """Generate canonical URL from category and slug."""
        return f'https://fromfirstprinciples.com/{self.category}/{self.slug}'

    @computed_field
    @property
    def has_math(self) -> bool:
        """Check if content contains mathematical notation."""
        return self.content.get('has_math', False)

    @computed_field
    @property
    def has_code(self) -> bool:
        """Check if content contains code examples."""
        return self.content.get('has_code', False)

    @computed_field
    @property
    def difficulty_level(self) -> str:
        """Get content difficulty level."""
        return self.content.get('difficulty_level', 'beginner')

    @computed_field
    @property
    def related_posts(self) -> List[str]:
        """Get related post slugs."""
        return self.content.get('related_posts', [])


class ContentChunk(BaseModel):
    """Individual content chunk for embedding and search."""

    # Unique identifier
    chunk_id: str = Field(..., description='Unique chunk identifier')

    # Source information
    post_slug: str = Field(..., description='Source post slug')
    category: str = Field(..., description='Content category')

    # Content
    content: str = Field(..., description='Chunk text content')
    chunk_index: int = Field(..., description='Index of chunk within post')

    # Position information
    start_char: int = Field(
        ..., description='Start character position in original text'
    )
    end_char: int = Field(..., description='End character position in original text')

    # Content analysis
    word_count: int = Field(..., description='Word count of this chunk')
    char_count: int = Field(..., description='Character count of this chunk')

    # Semantic information
    section_title: Optional[str] = Field(
        None, description='Section title if applicable'
    )
    paragraph_index: Optional[int] = Field(
        None, description='Paragraph index within post'
    )

    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def content_hash(self) -> str:
        """Generate hash of chunk content for change detection."""
        return hashlib.md5(self.content.encode()).hexdigest()

    @validator('content')
    def validate_content_not_empty(cls, v):
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class EmbeddingVector(BaseModel):
    """Vector embedding for a content chunk."""

    # Reference to source chunk
    chunk_id: str = Field(..., description='Reference to ContentChunk')

    # Embedding data
    vector: List[float] = Field(..., description='Embedding vector')
    vector_dim: int = Field(..., description='Dimension of embedding vector')

    # Model information
    model_name: str = Field(..., description='Model used for embedding')
    model_version: Optional[str] = Field(None, description='Model version')

    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = Field(
        None, description='Time taken to generate embedding'
    )

    @validator('vector')
    def validate_vector_not_empty(cls, v):
        """Ensure vector is not empty."""
        if not v:
            raise ValueError('Vector cannot be empty')
        return v

    @computed_field
    @property
    def vector_hash(self) -> str:
        """Generate hash of vector for deduplication."""
        vector_str = ','.join(map(str, self.vector))
        return hashlib.md5(vector_str.encode()).hexdigest()


class BlogPost(BaseModel):
    """Complete blog post with content and metadata."""

    # File system information
    directory_path: str = Field(..., description='Path to post directory')
    markdown_file: str = Field(..., description='Path to markdown file')
    metadata_file: str = Field(..., description='Path to metadata file')

    # Content and metadata
    metadata: ContentMetadata = Field(..., description='Post metadata')
    raw_content: str = Field(..., description='Raw markdown content')
    processed_content: str = Field(..., description='Processed plain text content')

    # Content chunks
    chunks: List[ContentChunk] = Field(
        default_factory=list, description='Content chunks'
    )

    # File metadata
    file_size_bytes: int = Field(..., description='File size in bytes')
    file_modified_time: datetime = Field(..., description='File modification time')

    # Processing metadata
    indexed_at: Optional[datetime] = Field(None, description='When post was indexed')
    processing_errors: List[str] = Field(
        default_factory=list, description='Processing errors'
    )

    @computed_field
    @property
    def content_hash(self) -> str:
        """Generate hash of content for change detection."""
        content_to_hash = f'{self.raw_content}{self.metadata.model_dump_json()}'
        return hashlib.sha256(content_to_hash.encode()).hexdigest()

    @computed_field
    @property
    def chunk_count(self) -> int:
        """Get number of chunks for this post."""
        return len(self.chunks)

    @computed_field
    @property
    def total_word_count(self) -> int:
        """Calculate total word count from chunks."""
        return sum(chunk.word_count for chunk in self.chunks)

    @validator('raw_content')
    def validate_content_not_empty(cls, v):
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v


class IndexingResult(BaseModel):
    """Result of indexing operation."""

    # Operation metadata
    operation_id: str = Field(..., description='Unique operation identifier')
    started_at: datetime = Field(..., description='Operation start time')
    completed_at: Optional[datetime] = Field(
        None, description='Operation completion time'
    )

    # Results
    posts_processed: int = Field(default=0, description='Number of posts processed')
    posts_updated: int = Field(default=0, description='Number of posts updated')
    posts_skipped: int = Field(default=0, description='Number of posts skipped')
    chunks_created: int = Field(default=0, description='Number of chunks created')
    embeddings_generated: int = Field(
        default=0, description='Number of embeddings generated'
    )

    # Performance metrics
    total_processing_time_ms: Optional[float] = Field(
        None, description='Total processing time'
    )
    average_time_per_post_ms: Optional[float] = Field(
        None, description='Average time per post'
    )

    # Errors and warnings
    errors: List[str] = Field(default_factory=list, description='Processing errors')
    warnings: List[str] = Field(default_factory=list, description='Processing warnings')

    # Status
    status: str = Field(default='running', description='Operation status')

    @validator('status')
    def validate_status(cls, v):
        """Validate status is one of the allowed values."""
        allowed_statuses = ['running', 'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

    @computed_field
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate operation duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate of processing."""
        total = self.posts_processed + self.posts_skipped
        if total == 0:
            return 0.0
        return self.posts_processed / total


class SearchQuery(BaseModel):
    """Search query with parameters."""

    # Query text
    query: str = Field(..., description='Search query text')

    # Search parameters
    limit: int = Field(default=10, description='Maximum number of results')
    offset: int = Field(default=0, description='Offset for pagination')

    # Filtering
    categories: Optional[List[str]] = Field(None, description='Filter by categories')
    tags: Optional[List[str]] = Field(None, description='Filter by tags')
    difficulty_levels: Optional[List[str]] = Field(
        None, description='Filter by difficulty'
    )
    date_from: Optional[str] = Field(
        None, description='Filter by date from (YYYY-MM-DD)'
    )
    date_to: Optional[str] = Field(None, description='Filter by date to (YYYY-MM-DD)')

    # Search type
    search_type: str = Field(
        default='hybrid', description='Search type: keyword, semantic, hybrid'
    )

    # Scoring weights for hybrid search
    keyword_weight: float = Field(
        default=0.3, description='Weight for keyword matching'
    )
    semantic_weight: float = Field(
        default=0.7, description='Weight for semantic similarity'
    )

    @validator('search_type')
    def validate_search_type(cls, v):
        """Validate search type."""
        allowed_types = ['keyword', 'semantic', 'hybrid']
        if v not in allowed_types:
            raise ValueError(f'Search type must be one of {allowed_types}')
        return v

    @validator('keyword_weight', 'semantic_weight')
    def validate_weights(cls, v):
        """Validate weights are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError('Weights must be between 0 and 1')
        return v


class SearchResult(BaseModel):
    """Individual search result."""

    # Source information
    post_slug: str = Field(..., description='Source post slug')
    category: str = Field(..., description='Content category')
    chunk_id: Optional[str] = Field(None, description='Matching chunk ID if applicable')

    # Content
    title: str = Field(..., description='Post title')
    excerpt: str = Field(..., description='Relevant excerpt')
    content_snippet: Optional[str] = Field(None, description='Matching content snippet')

    # Metadata
    author: str = Field(..., description='Post author')
    publish_date: str = Field(..., description='Publication date')
    tags: List[str] = Field(default_factory=list, description='Post tags')

    # Scoring
    relevance_score: float = Field(..., description='Overall relevance score')
    keyword_score: Optional[float] = Field(None, description='Keyword matching score')
    semantic_score: Optional[float] = Field(
        None, description='Semantic similarity score'
    )

    # URLs
    url: str = Field(..., description='Post URL')

    @computed_field
    @property
    def normalized_score(self) -> float:
        """Normalize relevance score to 0-1 range."""
        return max(0.0, min(1.0, self.relevance_score))


class SearchResponse(BaseModel):
    """Complete search response."""

    # Query information
    query: SearchQuery = Field(..., description='Original search query')

    # Results
    results: List[SearchResult] = Field(
        default_factory=list, description='Search results'
    )

    # Metadata
    total_results: int = Field(..., description='Total number of matching results')
    results_returned: int = Field(..., description='Number of results in this response')
    processing_time_ms: float = Field(..., description='Search processing time')

    # Pagination
    has_more: bool = Field(..., description='Whether more results are available')
    next_offset: Optional[int] = Field(None, description='Offset for next page')

    @computed_field
    @property
    def page_info(self) -> Dict[str, int]:
        """Get pagination information."""
        return {
            'current_page': (self.query.offset // self.query.limit) + 1,
            'total_pages': (self.total_results + self.query.limit - 1)
            // self.query.limit,
            'results_per_page': self.query.limit,
        }
