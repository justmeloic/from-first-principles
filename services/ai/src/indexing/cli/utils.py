"""Shared utilities for CLI commands."""

from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..builder import IndexingPipeline
from ..config import IndexingConfig

# Rich console for better output
console = Console()


def get_pipeline() -> IndexingPipeline:
    """Get a configured indexing pipeline instance."""
    try:
        config = IndexingConfig()
        return IndexingPipeline(config)
    except Exception as e:
        rprint(f'[red]❌ Failed to initialize pipeline: {e}[/red]')
        raise typer.Exit(1)


def create_progress() -> Progress:
    """Create a consistent progress bar for CLI operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    )


def handle_error(operation: str, error: Exception) -> None:
    """Handle and display errors consistently."""
    rprint(f'[red]❌ {operation} failed: {error}[/red]')
    raise typer.Exit(1)


def validate_slug_category(slug: Optional[str], category: Optional[str]) -> None:
    """Validate that category is provided when slug is specified."""
    if slug and not category:
        rprint('[red]❌ When specifying --slug, you must also specify --category[/red]')
        raise typer.Exit(1)


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way."""
    if seconds < 60:
        return f'{seconds:.2f} seconds'
    elif seconds < 3600:
        minutes = seconds / 60
        return f'{minutes:.1f} minutes'
    else:
        hours = seconds / 3600
        return f'{hours:.1f} hours'
