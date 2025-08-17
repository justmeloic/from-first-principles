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

"""Request schemas for the root agent API.

This module defines the Pydantic models for validating incoming API requests.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Query(BaseModel):
    """Represents a query from a user to the agent."""

    text: str = Field(..., min_length=1, description="The user's query text")
    model: Optional[str] = Field(
        default=None,
        description='Model to use for this query. If not provided, uses default',
    )
    file_artifacts: Optional[List[str]] = Field(
        default=None,
        description='List of artifact IDs for files uploaded with this message',
    )

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validates that text is not empty or just whitespace."""
        if not v.strip():
            raise ValueError('Text must not be empty or just whitespace')
        return v.strip()

    @field_validator('model')
    @classmethod
    def validate_model(cls, v: Optional[str]) -> Optional[str]:
        """Validates that the model is supported if provided."""
        if v is not None:
            # Import here to avoid circular imports
            from src.app.core.config import settings

            if v not in settings.AVAILABLE_MODELS:
                available = list(settings.AVAILABLE_MODELS.keys())
                raise ValueError(
                    f'Model "{v}" not supported. Available models: {available}'
                )
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            'example': {
                'text': 'What are the latest developments in AI?',
                'model': 'gemini-2.5-pro',
            }
        }


class SearchQuery(BaseModel):
    """Represents a search query for content."""

    query: str = Field(..., min_length=1, description='The search query text')
    search_type: str = Field(
        default='semantic',
        description='Search type: semantic, keyword, or hybrid',
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description='Maximum number of results to return',
    )
    category_filter: Optional[str] = Field(
        default=None,
        description='Filter by category: blog or engineering',
    )
    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description='Minimum similarity score for semantic search',
    )
    case_sensitive: bool = Field(
        default=False,
        description='Whether keyword search should be case sensitive',
    )

    @field_validator('query')
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        """Validates that query is not empty or just whitespace."""
        if not v.strip():
            raise ValueError('Query must not be empty or just whitespace')
        return v.strip()

    @field_validator('search_type')
    @classmethod
    def validate_search_type(cls, v: str) -> str:
        """Validates that search type is supported."""
        allowed_types = ['semantic', 'keyword', 'hybrid']
        if v not in allowed_types:
            raise ValueError(f'Search type must be one of {allowed_types}')
        return v

    @field_validator('category_filter')
    @classmethod
    def validate_category_filter(cls, v: Optional[str]) -> Optional[str]:
        """Validates that category filter is supported if provided."""
        if v is not None:
            allowed_categories = ['blog', 'engineering']
            if v not in allowed_categories:
                raise ValueError(f'Category filter must be one of {allowed_categories}')
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            'example': {
                'query': 'machine learning concepts',
                'search_type': 'semantic',
                'limit': 5,
                'category_filter': 'blog',
                'similarity_threshold': 0.7,
                'case_sensitive': False,
            }
        }
