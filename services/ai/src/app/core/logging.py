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

"""Logging configuration."""

import logging
import sys
from pathlib import Path

from loguru import logger as _logger

from src.app.core.config import settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging and route to loguru."""

    def emit(self, record):
        """Emit log record."""
        # Get corresponding Loguru level if it exists
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Setup logging configuration."""
    # Remove default handlers
    _logger.remove()

    # Add console handler
    _logger.add(
        sys.stdout,
        colorize=True,
        format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
        '<level>{level: <8}</level> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
        '<level>{message}</level>',
        level='DEBUG' if settings.DEBUG else settings.LOG_LEVEL,
    )

    # Add file handler for production
    if settings.ENVIRONMENT == 'production':
        # Ensure logs directory exists
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)

        _logger.add(
            'logs/app.log',
            rotation='500 MB',
            retention='10 days',
            compression='gz',
            format=(
                '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | '
                '{name}:{function}:{line} | {message}'
            ),
            level='INFO',
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set up loggers for common libraries
    for logger_name in ['uvicorn', 'uvicorn.error', 'uvicorn.access', 'fastapi']:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
