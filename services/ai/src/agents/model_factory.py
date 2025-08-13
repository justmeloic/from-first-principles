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

"""Model factory for creating AI models based on configuration."""

import os
from typing import Union

from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm

try:
    from ..app.core.config import settings
except ImportError:
    # Handle direct script execution
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from app.core.config import settings


def create_model(model_name: str) -> Union[Gemini, LiteLlm]:
    """Create and return a model instance based on the provider configuration.

    Args:
        model_name: The name of the model to create
            (e.g., 'gemini-2.5-flash', 'mistral-small3.1')

    Returns:
        A model instance (either Gemini or LiteLlm)

    Raises:
        ValueError: If the model provider is not supported or model is not found
        RuntimeError: If required environment variables are not set for Ollama
    """
    model_config = settings.AVAILABLE_MODELS.get(model_name)

    if not model_config:
        raise ValueError(f"Model '{model_name}' not found in AVAILABLE_MODELS")

    provider = model_config['provider']

    if provider == 'gemini':
        return Gemini(model=model_name)

    elif provider == 'ollama':
        # Set the required environment variable for Ollama
        os.environ['OLLAMA_API_BASE'] = settings.OLLAMA_API_BASE

        # Verify Ollama is accessible (optional, but good for debugging)
        try:
            # Use ollama_chat provider as recommended in the documentation
            ollama_model_name = f'ollama_chat/{model_name}'
            return LiteLlm(model=ollama_model_name)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create Ollama model '{model_name}'. "
                f'Make sure Ollama is running at {settings.OLLAMA_API_BASE} '
                f'and the model is available. Error: {e}'
            )

    else:
        raise ValueError(f'Unsupported model provider: {provider}')


def get_default_model() -> Union[Gemini, LiteLlm]:
    """Get the default model based on the configured provider.

    Returns:
        A model instance for the default model
    """
    if settings.MODEL_PROVIDER == 'gemini':
        return create_model(settings.GEMINI_MODEL)
    elif settings.MODEL_PROVIDER == 'ollama':
        return create_model(settings.OLLAMA_MODEL)
    else:
        raise ValueError(f'Unsupported MODEL_PROVIDER: {settings.MODEL_PROVIDER}')


def get_pro_model() -> Union[Gemini, LiteLlm]:
    """Get the pro/advanced model based on the configured provider.

    Returns:
        A model instance for the pro model
    """
    if settings.MODEL_PROVIDER == 'gemini':
        return create_model(settings.GEMINI_MODEL_PRO)
    elif settings.MODEL_PROVIDER == 'ollama':
        return create_model(settings.OLLAMA_MODEL_PRO)
    else:
        raise ValueError(f'Unsupported MODEL_PROVIDER: {settings.MODEL_PROVIDER}')
