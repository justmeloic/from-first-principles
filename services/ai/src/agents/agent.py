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
information when needed. The agent can use either Gemini or Ollama models
based on the configuration.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from .model_factory import get_pro_model
from .system_instructions import get_general_assistant_instructions

root_agent = Agent(
    name='general_assistant',
    model=get_pro_model(),
    description=(
        'A knowledgeable AI assistant for "From First Principles" that can '
        'help users navigate content, dive deeper into topics, and discover '
        'insights from the knowledge base using Google search when needed.'
    ),
    instruction=get_general_assistant_instructions(),
    tools=[google_search],
)
