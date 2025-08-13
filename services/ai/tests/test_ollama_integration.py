#!/usr/bin/env python3
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

"""Test script to verify Ollama model integration works correctly."""

import os
import sys

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.model_factory import create_model, get_default_model, get_pro_model
from app.core.config import settings


def test_model_creation():
    """Test creating models for different providers."""
    print(f'Current MODEL_PROVIDER: {settings.MODEL_PROVIDER}')
    print(f'Ollama API Base: {settings.OLLAMA_API_BASE}')
    print(f'Available models: {list(settings.AVAILABLE_MODELS.keys())}')
    print()

    # Test Gemini models
    print('Testing Gemini models...')
    try:
        gemini_model = create_model('gemini-2.5-flash')
        print(f'✓ Created Gemini model: {gemini_model.model}')
    except Exception as e:
        print(f'✗ Failed to create Gemini model: {e}')

    # Test Ollama models
    print('\nTesting Ollama models...')
    try:
        ollama_model = create_model('mistral-small3.1')
        print(f'✓ Created Ollama model: {ollama_model.model}')
    except Exception as e:
        print(f'✗ Failed to create Ollama model: {e}')

    # Test default model based on provider
    print(f'\nTesting default model (provider: {settings.MODEL_PROVIDER})...')
    try:
        default_model = get_default_model()
        print(f'✓ Created default model: {default_model.model}')
    except Exception as e:
        print(f'✗ Failed to create default model: {e}')

    # Test pro model based on provider
    print(f'\nTesting pro model (provider: {settings.MODEL_PROVIDER})...')
    try:
        pro_model = get_pro_model()
        print(f'✓ Created pro model: {pro_model.model}')
    except Exception as e:
        print(f'✗ Failed to create pro model: {e}')


def test_agent_creation():
    """Test creating the agent with the current configuration."""
    print('\n' + '=' * 50)
    print('Testing agent creation...')
    try:
        from agents.agent import root_agent

        print(f'✓ Created agent: {root_agent.name}')
        print(f'  Model: {root_agent.model.model}')
        print(f'  Tools: {[tool.__name__ for tool in root_agent.tools]}')
    except Exception as e:
        print(f'✗ Failed to create agent: {e}')


if __name__ == '__main__':
    print('Ollama Model Integration Test')
    print('=' * 50)
    test_model_creation()
    test_agent_creation()
