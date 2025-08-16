"""
Configuration for the analytics dashboard.

This module provides configuration management for the dashboard,
including environment variable handling and default settings.
"""

import os
from pathlib import Path


class AnalyticsConfig:
    """Configuration settings for the analytics dashboard."""

    def __init__(self):
        """Initialize configuration from environment variables."""

        # Data paths
        self.data_dir = Path(os.getenv("ANALYTICS_DATA_DIR", "data"))
        self.logs_dir = Path(os.getenv("ANALYTICS_LOGS_DIR", "logs"))

        # Dashboard settings
        self.default_port = int(os.getenv("ANALYTICS_PORT", "8501"))
        self.default_host = os.getenv("ANALYTICS_HOST", "localhost")

        # Performance settings
        self.max_log_entries = int(os.getenv("ANALYTICS_MAX_LOG_ENTRIES", "10000"))
        self.cache_ttl = int(os.getenv("ANALYTICS_CACHE_TTL", "300"))  # 5 minutes

        # Feature flags
        self.enable_debug = os.getenv("ANALYTICS_DEBUG", "false").lower() == "true"
        self.enable_profiling = (
            os.getenv("ANALYTICS_PROFILING", "false").lower() == "true"
        )

        # Chart settings
        self.default_chart_height = int(os.getenv("ANALYTICS_CHART_HEIGHT", "400"))
        self.max_tags_display = int(os.getenv("ANALYTICS_MAX_TAGS", "20"))

    def get_data_path(self, subpath: str) -> Path:
        """Get path relative to data directory."""
        return self.data_dir / subpath

    def get_logs_path(self, filename: str) -> Path:
        """Get path relative to logs directory."""
        return self.logs_dir / filename

    @property
    def content_dir(self) -> Path:
        """Get content directory path."""
        return self.get_data_path("content")

    @property
    def lancedb_dir(self) -> Path:
        """Get LanceDB directory path."""
        return self.get_data_path("lancedb")

    def validate_paths(self) -> dict:
        """Validate that required paths exist."""
        validation = {}

        validation["data_dir"] = {
            "path": self.data_dir,
            "exists": self.data_dir.exists(),
            "readable": self.data_dir.is_dir() if self.data_dir.exists() else False
        }

        validation["content_dir"] = {
            "path": self.content_dir,
            "exists": self.content_dir.exists(),
            "readable": (
                self.content_dir.is_dir() if self.content_dir.exists() else False
            )
        }

        validation["lancedb_dir"] = {
            "path": self.lancedb_dir,
            "exists": self.lancedb_dir.exists(),
            "readable": (
                self.lancedb_dir.is_dir() if self.lancedb_dir.exists() else False
            )
        }

        validation["logs_dir"] = {
            "path": self.logs_dir,
            "exists": self.logs_dir.exists(),
            "readable": self.logs_dir.is_dir() if self.logs_dir.exists() else False
        }

        return validation


# Global configuration instance
config = AnalyticsConfig()
