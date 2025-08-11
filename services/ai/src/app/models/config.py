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

"""Configuration models for the root agent.

This module defines the configuration and domain models used by the agent.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for an agent service."""

    app_name: str = Field(
        default='agent_app', description='Name of the agent application'
    )
    user_id: str = Field(
        default='default_user', description='User identifier for the session'
    )
    max_tokens: int = Field(
        default=4096,
        ge=1,
        le=8192,
        description='Maximum number of tokens in the response',
    )
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description='Temperature for response generation'
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            'example': {
                'app_name': 'root_agent',
                'user_id': 'user123',
                'max_tokens': 2048,
                'temperature': 0.1,
            }
        }
