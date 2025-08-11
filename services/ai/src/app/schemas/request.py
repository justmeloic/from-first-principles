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

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Query(BaseModel):
    """Represents a query from a user to the agent."""

    text: str = Field(..., min_length=1, description="The user's query text")
    model: Optional[str] = Field(
        default=None,
        description='Model to use for this query. If not provided, uses default',
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
