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

This module configures and instantiates Loïc's personal AI agent that
represents him professionally and provides information about his background,
expertise, and experience to recruiters and visitors. The agent can use
Google search to find additional information when needed.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from .model_factory import get_pro_model
from .system_instructions import get_personal_agent_instructions

root_agent = Agent(
    name='personal_agent',
    model=get_pro_model(),
    description=(
        "Loïc Muhirwa's personal AI agent. I represent Loïc and provide "
        'accurate information about his background, expertise, and experience '
        'to recruiters, hiring managers, and visitors.'
    ),
    instruction=get_personal_agent_instructions(),
    tools=[google_search],
)
