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

"""Configuration module for the application."""

from typing import List

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_settings import BaseSettings


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str
    port: int
    log_level: str


class ApiConfig(BaseModel):
    """API configuration."""

    title: str
    description: str
    version: str


class CorsConfig(BaseModel):
    """CORS configuration."""

    allow_origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]
    expose_headers: List[str]


class ModelConfig(BaseModel):
    """Model configuration."""

    gemini_version: str


class Settings(BaseSettings):
    """Core application settings."""

    # Loïc: perhaps confusingly, The "model" in model_config refers to the
    # Pydantic data model Unfortunately, we can't rename model_config
    # because it's the specific name Pydantic V2 looks for to apply its configuration.
    model_config = ConfigDict(env_file='.env', case_sensitive=True, extra='ignore')

    # Pydantic's BaseSettings automatically treats
    # variables with no default values as required

    HOST: str = '0.0.0.0'
    PORT: int = 8081
    LOG_LEVEL: str = 'INFO'
    DEBUG: bool = False
    ENVIRONMENT: str = 'development'

    # API settings
    API_TITLE: str = 'AgentChat API'
    API_DESCRIPTION: str = 'API for interacting with multi-model AI agents'
    API_VERSION: str = '1.0.0'

    # Frontend URL for CORS
    FRONTEND_URL: str = 'http://localhost:3000'

    # Model settings
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    GEMINI_MODEL_PRO: str = 'gemini-2.5-pro'
    DEFAULT_MODEL: str = 'gemini-2.5-flash'

    # Model provider settings
    MODEL_PROVIDER: str = 'gemini'  # 'gemini' or 'ollama'

    # Ollama settings
    OLLAMA_API_BASE: str = 'http://localhost:11434'
    OLLAMA_MODEL: str = 'mistral-small3.1'
    OLLAMA_MODEL_PRO: str = 'llama3.2'

    # Authentication settings
    AUTH_SECRET: str
    SESSION_TIMEOUT_HOURS: int = 24

    # Model configuration
    AVAILABLE_MODELS: dict = {
        'gemini-2.5-flash': {
            'name': 'gemini-2.5-flash',
            'display_name': 'Gemini 2.5 Flash',
            'description': "Google's latest fast model with improved capabilities",
            'max_tokens': 4096,
            'supports_tools': True,
            'default_temperature': 0.1,
            'provider': 'gemini',
        },
        'gemini-2.5-pro': {
            'name': 'gemini-2.5-pro',
            'display_name': 'Gemini 2.5 Pro',
            'description': "Google's latest high-quality model for complex reasoning",
            'max_tokens': 8192,
            'supports_tools': True,
            'default_temperature': 0.1,
            'provider': 'gemini',
        },
        'mistral-small3.1': {
            'name': 'mistral-small3.1',
            'display_name': 'Mistral Small 3.1',
            'description': 'Mistral Small model with tool support',
            'max_tokens': 4096,
            'supports_tools': False,  # Temporarily disable tools
            'default_temperature': 0.1,
            'provider': 'ollama',
        },
        'llama3.2': {
            'name': 'llama3.2',
            'display_name': 'Llama 3.2',
            'description': 'Meta Llama 3.2 model',
            'max_tokens': 4096,
            'supports_tools': False,  # Temporarily disable tools
            'default_temperature': 0.1,
            'provider': 'ollama',
        },
    }

    # Development settings
    RESTART_SCRIPT_PATH: str = './scripts/restart-server.sh'

    @field_validator('MODEL_PROVIDER', mode='before')
    @classmethod
    def validate_model_provider(cls, v: str) -> str:
        """Validate model provider is one of the allowed values."""
        allowed_providers = ['gemini', 'ollama']
        if v.lower() not in allowed_providers:
            raise ValueError(f'MODEL_PROVIDER must be one of {allowed_providers}')
        return v.lower()

    @field_validator('LOG_LEVEL', mode='before')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'LOG_LEVEL must be one of {allowed_levels}')
        return v.upper()

    @property
    def server(self) -> ServerConfig:
        """Get server configuration."""
        return ServerConfig(
            host=self.HOST,
            port=self.PORT,
            log_level=self.LOG_LEVEL,
        )

    @property
    def api(self) -> ApiConfig:
        """Get API configuration."""
        return ApiConfig(
            title=self.API_TITLE,
            description=self.API_DESCRIPTION,
            version=self.API_VERSION,
        )

    @property
    def cors(self) -> CorsConfig:
        """Get CORS configuration."""
        # Support multiple origins separated by commas
        origins = [url.strip() for url in self.FRONTEND_URL.split(',') if url.strip()]
        return CorsConfig(
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=['GET', 'POST', 'OPTIONS'],
            allow_headers=['*', 'X-Session-ID'],
            expose_headers=['X-Session-ID'],
        )

    @property
    def model(self) -> ModelConfig:
        """Get model configuration."""
        return ModelConfig(
            gemini_version=self.GEMINI_MODEL,
        )


settings = Settings()
