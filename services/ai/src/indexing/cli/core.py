"""Core indexing and testing commands."""

from typing import Optional

import typer
from rich import print as rprint
from rich.table import Table

from .utils import console, create_progress, get_pipeline, handle_error


def test_pipeline():
    """
    🧪 Test the indexing pipeline configuration and dependencies.

    Validates that all components are working correctly:
    • ✅ Embedding model loading and functionality
    • ✅ Content directory access and blog post detection
    • ✅ Database connectivity and table setup
    • ✅ Text processing and chunking capabilities

    This command verifies that all components are working correctly.
    Run this first when setting up or troubleshooting the system.

    Example:
      index-cli test
    """
    rprint('[blue]🧪 Testing indexing pipeline...[/blue]')

    with create_progress() as progress:
        task = progress.add_task('Running pipeline tests...', total=None)

        try:
            pipeline = get_pipeline()
            result = pipeline.quick_test()

            progress.update(task, completed=True)

            if result.get('success'):
                rprint('[green]✅ Pipeline test successful![/green]')

                # Display test results in a nice table
                table = Table(title='Test Results')
                table.add_column('Component', style='cyan')
                table.add_column('Status', style='green')
                table.add_column('Details')

                for component, status in result.get('components', {}).items():
                    status_icon = '✅' if status.get('success') else '❌'
                    details = status.get('details', '')
                    table.add_row(component.title(), status_icon, details)

                console.print(table)
            else:
                rprint('[red]❌ Pipeline test failed![/red]')
                error = result.get('error', 'Unknown error')
                rprint(f'[red]Error: {error}[/red]')
                raise typer.Exit(1)

        except Exception as e:
            progress.update(task, completed=True)
            handle_error('Test', e)


def index_content(
    category: Optional[str] = None,
    slug: Optional[str] = None,
    force: bool = False,
):
    """
    📚 Index blog content for search.

    Processes blog posts and generates vector embeddings for semantic search.

    Options:
    • Index all content: Run without parameters to index everything
    • Index by category: Use --category to index only 'blog' or 'engineering' posts
    • Index single post: Use both --category and --slug for a specific post
    • Force reindex: Use --force to reprocess already indexed content

    The indexing process:
    1. 📄 Loads blog posts from content directories
    2. ✂️  Splits content into searchable chunks
    3. 🧠 Generates AI embeddings for semantic similarity
    4. 💾 Stores everything in the vector database

    Examples:
      index-cli index                           # Index all content
      index-cli index -c blog                   # Index only blog posts
      index-cli index -c blog -s my-post        # Index specific post
      index-cli index --force                   # Force reindex all
    """
    pipeline = get_pipeline()

    if slug and not category:
        rprint('[red]❌ When specifying --slug, you must also specify --category[/red]')
        raise typer.Exit(1)

    with create_progress() as progress:
        if slug:
            # Index single post
            task = progress.add_task(f'Indexing {category}/{slug}...', total=None)
            rprint(f'[blue]📄 Indexing post: {category}/{slug}[/blue]')

            try:
                result = pipeline.index_single_post(category, slug)  # type: ignore
                progress.update(task, completed=True)

                if result and result.posts_processed > 0:
                    rprint('[green]✅ Post indexed successfully![/green]')
                    rprint(f'[dim]Chunks created: {result.chunks_created}[/dim]')
                    rprint(
                        f'[dim]Embeddings generated: '
                        f'{result.embeddings_generated}[/dim]'
                    )
                else:
                    rprint('[red]❌ Failed to index post[/red]')
                    if result and result.errors:
                        for error in result.errors:
                            rprint(f'[red]Error: {error}[/red]')
                    raise typer.Exit(1)

            except Exception as e:
                progress.update(task, completed=True)
                handle_error('Indexing', e)

        else:
            # Index all or category
            if category:
                task = progress.add_task(f'Indexing {category} posts...', total=None)
                rprint(f'[blue]📚 Indexing category: {category}[/blue]')
            else:
                task = progress.add_task('Indexing all posts...', total=None)
                rprint('[blue]📚 Indexing all blog posts...[/blue]')

            try:
                result = pipeline.index_all_content(
                    category_filter=category, force_reindex=force
                )
                progress.update(task, completed=True)

                rprint('[green]✅ Indexing completed![/green]')

                # Display results in a table
                table = Table(title='Indexing Results')
                table.add_column('Metric', style='cyan')
                table.add_column('Count', style='green')

                table.add_row('Posts processed', str(result.posts_processed))
                table.add_row('Posts updated', str(result.posts_updated))
                table.add_row('Posts skipped', str(result.posts_skipped))
                table.add_row('Chunks created', str(result.chunks_created))
                table.add_row('Embeddings generated', str(result.embeddings_generated))

                console.print(table)

                if result.errors:
                    rprint(f'[yellow]⚠️  {len(result.errors)} errors occurred:[/yellow]')
                    for error in result.errors[:3]:  # Show first 3 errors
                        rprint(f'[yellow]  - {error}[/yellow]')
                    if len(result.errors) > 3:
                        rprint(f'[dim]  ... and {len(result.errors) - 3} more[/dim]')

                if result.duration_seconds:
                    rprint(
                        f'[dim]Processing time: '
                        f'{result.duration_seconds:.2f} seconds[/dim]'
                    )

            except Exception as e:
                progress.update(task, completed=True)
                handle_error('Indexing', e)


def clear_index(category: Optional[str] = None, confirm: bool = False):
    """
    🗑️  Clear the search index.

    Removes indexed content and embeddings from the database.
    ⚠️  This action cannot be undone!

    Options:
    • Clear all: Run without parameters to clear everything
    • Clear category: Use --category to clear only 'blog' or 'engineering'
    • Skip confirmation: Use --yes to skip the safety prompt

    After clearing, you'll need to run 'index-cli index' to rebuild the search database.

    Examples:
      index-cli clear                    # Clear everything (with confirmation)
      index-cli clear -c blog            # Clear only blog posts
      index-cli clear --yes              # Clear all without confirmation
    """
    if category:
        message = f'clear the [red]{category}[/red] category index'
    else:
        message = 'clear the [red]entire[/red] search index'

    if not confirm:
        confirmed = typer.confirm(f'Are you sure you want to {message}?')
        if not confirmed:
            rprint('[yellow]Operation cancelled.[/yellow]')
            return

    with create_progress() as progress:
        task = progress.add_task('Clearing index...', total=None)

        try:
            pipeline = get_pipeline()
            pipeline.clear_index(category=category)
            progress.update(task, completed=True)

            if category:
                rprint(f'[green]✅ Cleared {category} category index![/green]')
            else:
                rprint('[green]✅ Cleared entire index![/green]')

        except Exception as e:
            progress.update(task, completed=True)
            handle_error('Clear index', e)
