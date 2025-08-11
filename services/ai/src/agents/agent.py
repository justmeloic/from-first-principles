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

"""Defines the root agent for the application.

This module configures and instantiates a general-purpose AI assistant that
can help users with various queries and tasks using Google search to find
information when needed.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

try:
    from ..app.core.config import settings
    from .system_instructions import get_general_assistant_instructions
except ImportError:
    # Handle direct script execution (for quick testing)
    from system_instructions import get_general_assistant_instructions

    from src.app.core.config import settings


root_agent = Agent(
    name='general_assistant',
    model=settings.GEMINI_MODEL_PRO,
    description=(
        'A helpful general-purpose AI assistant that can answer questions '
        'and help with various tasks using Google search when needed.'
    ),
    instruction=get_general_assistant_instructions(),
    tools=[google_search],
)
