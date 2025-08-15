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

"""Response schemas for the root agent API.

This module defines the Pydantic models for API responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentReference(BaseModel):
    """Represents a reference used by the agent in its response."""

    source: str = Field(..., description='Source of the reference')
    page: Optional[int] = Field(None, description='Page number if applicable')
    section: Optional[str] = Field(None, description='Section reference')
    url: Optional[str] = Field(None, description='URL reference')


class AgentResponse(BaseModel):
    """Represents the agent's response to a user query."""

    response: str = Field(..., description="The agent's text response")
    references: Dict[str, Any] = Field(
        default_factory=dict, description='References and sources used by the agent'
    )
    session_id: Optional[str] = Field(None, description='Session identifier')
    model: Optional[str] = Field(None, description='Model used for this response')
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description='Confidence score of the response'
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            'example': {
                'response': (
                    'According to the latest research, AI development is advancing '
                    'rapidly in areas like multimodal understanding and reasoning.'
                ),
                'references': {
                    'arxiv_paper': 'Recent Advances in Large Language Models'
                },
                'session_id': 'abc123-def456-ghi789',
                'model': 'gemini-2.5-pro',
                'confidence': 0.95,
            }
        }


class SearchResult(BaseModel):
    """Represents a single search result."""

    title: str = Field(..., description='Title of the content')
    category: str = Field(..., description='Category of the content')
    slug: str = Field(..., description='URL slug of the content')
    excerpt: str = Field(..., description='Brief excerpt of the content')
    content: str = Field(..., description='Full content text')
    score: float = Field(..., description='Relevance score')
    url: str = Field(..., description='URL to the content')
    publish_date: str = Field(..., description='Publication date')
    tags: List[str] = Field(default_factory=list, description='Content tags')
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description='Additional metadata'
    )


class SearchResponse(BaseModel):
    """Represents the response to a search query."""

    query: Dict[str, Any] = Field(..., description='Original search query')
    results: List[SearchResult] = Field(
        default_factory=list, description='Search results'
    )
    total_results: int = Field(..., description='Total number of results')
    search_time_ms: float = Field(..., description='Search execution time in ms')
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description='Search metadata'
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            'example': {
                'query': {
                    'query': 'machine learning',
                    'search_type': 'semantic',
                    'limit': 5,
                },
                'results': [
                    {
                        'title': 'Introduction to Machine Learning',
                        'category': 'blog',
                        'slug': 'intro-to-ml',
                        'excerpt': (
                            'Machine learning is a subset of artificial intelligence...'
                        ),
                        'score': 0.95,
                        'url': '/blog/intro-to-ml',
                        'publish_date': '2024-01-15',
                        'tags': ['AI', 'ML', 'fundamentals'],
                    }
                ],
                'total_results': 1,
                'search_time_ms': 45.2,
                'metadata': {'search_type': 'semantic'},
            }
        }
