# Search Service Documentation

## Overview

The search service provides semantic and keyword search capabilities over indexed blog content. It leverages the indexing pipeline to offer fast, relevant search results with multiple search modes.

## API Endpoints

### 1. Search Content

**POST** `/api/v1/search/`

Search for content using semantic similarity or keyword matching.

#### Request Body

```json
{
  "query": "machine learning fundamentals",
  "search_type": "semantic",
  "limit": 5,
  "category_filter": "blog",
  "similarity_threshold": 0.7,
  "case_sensitive": false
}
```

#### Parameters

- `query` (string, required): The search query text
- `search_type` (string, optional): Search mode - "semantic", "keyword", or "hybrid" (default: "semantic")
- `limit` (integer, optional): Maximum results to return, 1-100 (default: 10)
- `category_filter` (string, optional): Filter by "blog" or "engineering" category
- `similarity_threshold` (float, optional): Minimum similarity score for semantic search, 0.0-1.0 (default: 0.5)
- `case_sensitive` (boolean, optional): Whether keyword search should be case sensitive (default: false)

#### Response

```json
{
  "query": {
    "query": "machine learning fundamentals",
    "search_type": "semantic",
    "limit": 5,
    "category_filter": "blog",
    "similarity_threshold": 0.7,
    "case_sensitive": false
  },
  "results": [
    {
      "title": "Introduction to Machine Learning",
      "category": "blog",
      "slug": "intro-to-ml",
      "excerpt": "Machine learning is a subset of artificial intelligence...",
      "content": "Full content text...",
      "score": 0.95,
      "url": "/blog/intro-to-ml",
      "publish_date": "2024-01-15",
      "tags": ["AI", "ML", "fundamentals"],
      "metadata": {
        "distance": 0.123,
        "term_matches": null
      }
    }
  ],
  "total_results": 1,
  "search_time_ms": 45.2,
  "metadata": {
    "search_type": "semantic",
    "threshold_applied": 0.7
  }
}
```

### 2. Search Statistics

**GET** `/api/v1/search/stats`

Get statistics about the search index.

#### Response

```json
{
  "database_available": true,
  "categories": {
    "blog": {
      "posts": 15,
      "chunks": 120,
      "last_updated": "2024-01-15T10:30:00"
    },
    "engineering": {
      "posts": 8,
      "chunks": 64,
      "last_updated": "2024-01-14T15:45:00"
    }
  },
  "total_chunks": 184,
  "database": {
    "location": "/path/to/database",
    "table_name": "blog_content",
    "size": "Unknown"
  },
  "embedding_info": {
    "model_name": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "device": "mps"
  }
}
```

### 3. Health Check

**GET** `/api/v1/search/health`

Check the health status of the search service.

#### Response

```json
{
  "status": "healthy",
  "pipeline_available": true,
  "database_available": true,
  "test_search_successful": true,
  "sample_results_count": 1
}
```

## Search Modes

### Semantic Search (Default)

Uses AI embeddings to find conceptually similar content, even if exact words don't match.

- Best for: Finding content by meaning and concepts
- Example: "AI concepts" might find content about "machine learning" and "neural networks"

### Keyword Search

Traditional text search for exact word/phrase matching.

- Best for: Finding specific terms or phrases
- Example: "Python tutorial" finds content containing those exact words

### Hybrid Search

Combines both semantic and keyword search results (if implemented).

## Usage Examples

### Basic Semantic Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "search_type": "semantic",
    "limit": 3
  }'
```

### Keyword Search with Category Filter

```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python programming",
    "search_type": "keyword",
    "limit": 5,
    "category_filter": "engineering",
    "case_sensitive": false
  }'
```

### High-Precision Semantic Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning neural networks",
    "search_type": "semantic",
    "similarity_threshold": 0.8,
    "limit": 3
  }'
```

## Integration with Frontend

The search service is designed to work seamlessly with frontend applications:

1. **Real-time Search**: Make requests as the user types
2. **Faceted Search**: Use category filters and search types
3. **Progressive Results**: Start with lower thresholds, refine as needed
4. **Error Handling**: Service returns structured error responses

## Performance Notes

- **Semantic Search**: Requires embedding generation (~100-500ms)
- **Keyword Search**: Faster, direct text matching (~10-50ms)
- **Caching**: Pipeline instance is cached for better performance
- **Scalability**: Uses LanceDB for efficient vector search

## Error Handling

All endpoints return structured error responses:

```json
{
  "detail": {
    "message": "Search failed",
    "error": "Database connection lost"
  }
}
```

Common HTTP status codes:

- `200`: Success
- `422`: Validation error (invalid request parameters)
- `500`: Internal server error (service unavailable, database issues)
