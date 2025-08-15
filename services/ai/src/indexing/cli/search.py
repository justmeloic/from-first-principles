"""Search and information commands."""

from typing import Optional

from rich import print as rprint
from rich.table import Table

from ..config import IndexingConfig
from .utils import console, create_progress, get_pipeline, handle_error


def search_content(
    query: str,
    limit: int = 5,
    category: Optional[str] = None,
    threshold: float = 0.5,
    mode: str = 'semantic',
    case_sensitive: bool = False,
):
    """
    🔍 Search indexed content.

    Supports both semantic search (AI-powered similarity) and keyword search
    (text matching).

    Search Modes:
    • 🧠 Semantic Mode (default): Uses AI embeddings to find conceptually
      similar content, even if exact words don't match
    • 🔍 Keyword Mode: Traditional text search for exact word/phrase matching

    Options:
    • --mode: Switch between 'semantic' (default) and 'keyword' search
    • --limit: Number of results to return (default: 5)
    • --category: Search only in 'blog' or 'engineering' posts
    • --threshold: Similarity cutoff for semantic search (default: 0.5)
    • --case-sensitive: Make keyword search case-sensitive

    Examples:
      index-cli search "machine learning"              # Semantic search
      index-cli search "exact phrase" -m keyword       # Keyword search
      index-cli search "AI" -c blog -l 3               # Blog posts only
      index-cli search "Python" -m keyword --case-sensitive  # Case sensitive
      index-cli search "concepts" -t 0.3               # Lower threshold
    """
    search_icon = '🧠' if mode == 'semantic' else '🔍'
    rprint(f'[blue]{search_icon} {mode.title()} search for: "{query}"[/blue]')

    with create_progress() as progress:
        task = progress.add_task('Searching...', total=None)

        try:
            pipeline = get_pipeline()
            results = pipeline.search_unified(
                query=query,
                mode=mode,
                limit=limit,
                category_filter=category,
                similarity_threshold=threshold,
                case_sensitive=case_sensitive,
            )
            progress.update(task, completed=True)

            if not results:
                rprint('[yellow]No results found.[/yellow]')
                return

            rprint(f'[green]Found {len(results)} results:[/green]\n')

            for i, result in enumerate(results, 1):
                rprint(f'[bold]{i}. {result.get("title", "Untitled")}[/bold]')

                # Show different score info based on search mode
                if mode == 'keyword':
                    score_info = (
                        f'Score: {result.get("score", 0):.3f} | '
                        f'Matches: {result.get("term_matches", 0)} terms'
                    )
                else:
                    score_info = f'Similarity: {result.get("score", 0):.3f}'

                rprint(
                    f'[dim]Category: {result.get("category", "Unknown")} | '
                    f'{score_info}[/dim]'
                )
                excerpt = result.get('excerpt', 'No excerpt available')[:200]
                rprint(f'{excerpt}...')
                category_path = result.get('category', '')
                slug_path = result.get('slug', '')
                rprint(f'[link]/{category_path}/{slug_path}[/link]\n')

        except Exception as e:
            progress.update(task, completed=True)
            handle_error('Search', e)


def show_stats():
    """
    📊 Show indexing statistics and database information.

    Displays comprehensive information about your indexed content:
    • 📈 Total posts and chunks indexed per category
    • 💾 Database location and table information
    • 🧠 Embedding model details and vector dimensions
    • ⏰ Last indexing timestamps
    • 📊 Content distribution across categories

    Use this to monitor indexing progress and database health.

    Example:
      index-cli stats
    """
    rprint('[blue]📊 Getting indexing statistics...[/blue]')

    with create_progress() as progress:
        task = progress.add_task('Loading statistics...', total=None)

        try:
            pipeline = get_pipeline()
            stats = pipeline.get_indexing_stats()
            progress.update(task, completed=True)

            # Display stats in a nice format
            table = Table(title='Database Statistics')
            table.add_column('Category', style='cyan')
            table.add_column('Posts', style='green')
            table.add_column('Chunks', style='green')
            table.add_column('Last Updated', style='dim')

            total_posts = 0
            total_chunks = 0

            for category, category_stats in stats.get('categories', {}).items():
                posts = category_stats.get('posts', 0)
                chunks = category_stats.get('chunks', 0)
                last_updated = category_stats.get('last_updated', 'Never')

                table.add_row(
                    category.title(), str(posts), str(chunks), str(last_updated)
                )
                total_posts += posts
                total_chunks += chunks

            table.add_row(
                '[bold]Total[/bold]',
                f'[bold]{total_posts}[/bold]',
                f'[bold]{total_chunks}[/bold]',
                '',
            )

            console.print(table)

            # Database info
            db_info = stats.get('database', {})
            if db_info:
                db_location = db_info.get('location', 'Unknown')
                db_size = db_info.get('size', 'Unknown')
                rprint(f'\n[dim]Database location: {db_location}[/dim]')
                rprint(f'[dim]Database size: {db_size}[/dim]')

        except Exception as e:
            progress.update(task, completed=True)
            handle_error('Get stats', e)


def show_config():
    """
    ⚙️  Show current configuration.

    Displays all current indexing and search configuration settings:
    • 📁 Content directories and file paths
    • 💾 Database connection and storage settings
    • 🧠 AI embedding model configuration
    • ✂️  Text chunking and processing parameters
    • 🔧 Performance and batch processing settings

    Use this to verify your setup and troubleshoot configuration issues.

    Example:
      index-cli config
    """
    try:
        config = IndexingConfig()

        table = Table(title='Indexing Configuration')
        table.add_column('Setting', style='cyan')
        table.add_column('Value', style='green')

        table.add_row('Content Directory', str(config.content.content_root))
        table.add_row('Database Path', str(config.database.db_path))
        table.add_row('Embedding Model', config.embedding.model_name)
        table.add_row('Chunk Size', str(config.chunking.chunk_size))
        table.add_row('Chunk Overlap', str(config.chunking.chunk_overlap))
        table.add_row('Batch Size', str(config.embedding.batch_size))
        table.add_row('Device', config.embedding.device)

        console.print(table)

        # Model info
        try:
            pipeline = get_pipeline()
            model_info = pipeline.embedder.get_model_info()
            embedding_dim = model_info.get('embedding_dimension', 'Unknown')
            rprint(f'\n[dim]Model Status: Loaded ({embedding_dim} dimensions)[/dim]')
        except Exception:
            rprint('\n[dim]Model Status: Not loaded[/dim]')

    except Exception as e:
        handle_error('Load config', e)
