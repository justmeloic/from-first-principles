"""
Blog Content Indexing CLI

A modern command-line interface for the blog content indexing pipeline.
Uses typer for a friendly CLI experience with rich output formatting.
"""

from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .builder import IndexingPipeline
from .config import IndexingConfig

# Create the main typer app
app = typer.Typer(
    name='index-cli',
    help="""
🔍 Blog Content Indexing Pipeline

Index and search your blog posts with AI-powered semantic search and traditional
keyword search.

Features:
  • 🧠 Semantic Search - AI-powered similarity matching using embeddings
  • 🔍 Keyword Search - Traditional text-based exact matching
  • 📚 Content Indexing - Process and store blog content with vector embeddings
  • 📊 Statistics - View indexing status and database information
  • 👀 Data Browsing - Inspect and explore indexed content
  • ⚙️  Configuration - Manage search and indexing settings

Quick Start:
  index-cli test                    # Test your setup
  index-cli index                   # Index all content
  index-cli search "your query"     # Search with AI similarity
  index-cli search "exact text" -m keyword  # Keyword search
  index-cli browse                  # Browse indexed data
  index-cli sample                  # View random samples
  index-cli inspect "post-slug"     # Deep dive into specific post
  index-cli stats                   # View statistics
    """,
    add_completion=False,
    rich_markup_mode='rich',
)

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


@app.command('test')
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

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
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
            rprint(f'[red]❌ Test failed: {e}[/red]')
            raise typer.Exit(1)


@app.command('index')
def index_content(
    category: Optional[str] = typer.Option(
        None, '--category', '-c', help='Index specific category (blog/engineering)'
    ),
    slug: Optional[str] = typer.Option(
        None, '--slug', '-s', help='Index specific post by slug'
    ),
    force: bool = typer.Option(
        False, '--force', '-f', help='Force reindex all content'
    ),
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

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
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
                        f'[dim]Embeddings generated: {result.embeddings_generated}[/dim]'
                    )
                else:
                    rprint('[red]❌ Failed to index post[/red]')
                    if result and result.errors:
                        for error in result.errors:
                            rprint(f'[red]Error: {error}[/red]')
                    raise typer.Exit(1)

            except Exception as e:
                progress.update(task, completed=True)
                rprint(f'[red]❌ Indexing failed: {e}[/red]')
                raise typer.Exit(1)

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
                        f'[dim]Processing time: {result.duration_seconds:.2f} seconds[/dim]'
                    )

            except Exception as e:
                progress.update(task, completed=True)
                rprint(f'[red]❌ Indexing failed: {e}[/red]')
                raise typer.Exit(1)


@app.command('stats')
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

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
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
                rprint(
                    f'\n[dim]Database location: {db_info.get("location", "Unknown")}[/dim]'
                )
                rprint(f'[dim]Database size: {db_info.get("size", "Unknown")}[/dim]')

        except Exception as e:
            progress.update(task, completed=True)
            rprint(f'[red]❌ Failed to get stats: {e}[/red]')
            raise typer.Exit(1)


@app.command('clear')
def clear_index(
    category: Optional[str] = typer.Option(
        None, '--category', '-c', help='Clear specific category only'
    ),
    confirm: bool = typer.Option(False, '--yes', '-y', help='Skip confirmation prompt'),
):
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

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
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
            rprint(f'[red]❌ Failed to clear index: {e}[/red]')
            raise typer.Exit(1)


@app.command('search')
def search_content(
    query: str = typer.Argument(..., help='Search query'),
    limit: int = typer.Option(5, '--limit', '-l', help='Number of results to show'),
    category: Optional[str] = typer.Option(
        None, '--category', '-c', help='Search in specific category only'
    ),
    threshold: float = typer.Option(
        0.5,
        '--threshold',
        '-t',
        help='Similarity threshold (0.0-1.0, lower = more permissive)',
    ),
    mode: str = typer.Option(
        'semantic',
        '--mode',
        '-m',
        help='Search mode: "semantic" for AI similarity, "keyword" for text matching',
    ),
    case_sensitive: bool = typer.Option(
        False, '--case-sensitive', help='Case sensitive keyword search'
    ),
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

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
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
                    score_info = f'Score: {result.get("score", 0):.3f} | Matches: {result.get("term_matches", 0)} terms'
                else:
                    score_info = f'Similarity: {result.get("score", 0):.3f}'

                rprint(
                    f'[dim]Category: {result.get("category", "Unknown")} | {score_info}[/dim]'
                )
                rprint(f'{result.get("excerpt", "No excerpt available")[:200]}...')
                rprint(
                    f'[link]/{result.get("category", "")}/{result.get("slug", "")}[/link]\n'
                )

        except Exception as e:
            progress.update(task, completed=True)
            rprint(f'[red]❌ Search failed: {e}[/red]')
            raise typer.Exit(1)


@app.command('browse')
def browse_data(
    limit: int = typer.Option(20, '--limit', '-l', help='Number of records to show'),
    category: Optional[str] = typer.Option(
        None, '--category', '-c', help='Filter by category (blog/engineering)'
    ),
    post: Optional[str] = typer.Option(
        None, '--post', '-p', help='Filter by post slug'
    ),
    columns: str = typer.Option(
        'title,category,post_slug,content',
        '--columns',
        help='Columns to display (comma-separated)',
    ),
):
    """
    👀 Browse indexed data in the database.

    View your indexed content in a table format with filtering options.
    This is useful for inspecting what's been indexed and debugging issues.

    Options:
    • --limit: Number of records to display (default: 20)
    • --category: Filter by content category
    • --post: Filter by specific post slug
    • --columns: Choose which columns to display

    Available columns:
      title, category, post_slug, content, chunk_index, word_count,
      created_at, model_name, vector_dim

    Examples:
      index-cli browse                              # Browse all data
      index-cli browse -c blog -l 10                # Blog posts only
      index-cli browse -p "my-post-slug"            # Specific post
      index-cli browse --columns "title,category,word_count"  # Custom columns
    """
    rprint('[blue]👀 Browsing indexed data...[/blue]')

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task('Loading data...', total=None)

        try:
            pipeline = get_pipeline()

            if not pipeline.content_table:
                rprint('[red]❌ No database table found. Run indexing first.[/red]')
                raise typer.Exit(1)

            # Build query
            query = pipeline.content_table.search()

            # Apply filters
            filters = []
            if category:
                filters.append(f"category = '{category}'")
            if post:
                filters.append(f"post_slug = '{post}'")

            if filters:
                query = query.where(' AND '.join(filters))

            # Get data
            results = query.limit(limit).to_list()
            progress.update(task, completed=True)

            if not results:
                rprint('[yellow]No data found with the specified filters.[/yellow]')
                return

            # Parse columns
            available_columns = [
                'title',
                'category',
                'post_slug',
                'content',
                'chunk_index',
                'word_count',
                'created_at',
                'model_name',
                'vector_dim',
            ]
            requested_columns = [col.strip() for col in columns.split(',')]
            display_columns = [
                col for col in requested_columns if col in available_columns
            ]

            if not display_columns:
                display_columns = ['title', 'category', 'post_slug', 'content']

            # Create table
            table = Table(title=f'Indexed Data ({len(results)} records)')

            for col in display_columns:
                style = 'cyan' if col in ['title', 'category'] else None
                table.add_column(col.title().replace('_', ' '), style=style)

            # Add rows
            for result in results:
                row_data = []
                for col in display_columns:
                    value = result.get(col, '')

                    # Truncate long content
                    if col == 'content' and isinstance(value, str) and len(value) > 100:
                        value = value[:97] + '...'
                    elif col == 'created_at' and value:
                        value = str(value)[:19]  # Remove microseconds

                    row_data.append(str(value))

                table.add_row(*row_data)

            console.print(table)

            # Show summary
            total_chunks = pipeline.content_table.count_rows()
            rprint(
                f'\n[dim]Showing {len(results)} of {total_chunks} total chunks[/dim]'
            )

        except Exception as e:
            progress.update(task, completed=True)
            rprint(f'[red]❌ Failed to browse data: {e}[/red]')
            raise typer.Exit(1)


@app.command('sample')
def sample_data(
    count: int = typer.Option(5, '--count', '-n', help='Number of random samples'),
    category: Optional[str] = typer.Option(
        None, '--category', '-c', help='Sample from specific category'
    ),
    show_vectors: bool = typer.Option(
        False, '--vectors', help='Show embedding vectors'
    ),
):
    """
    🎲 Show random samples from the indexed data.

    Get a quick overview of your indexed content by viewing random samples.
    Useful for understanding data quality and distribution.

    Options:
    • --count: Number of random samples to show (default: 5)
    • --category: Sample from specific category only
    • --vectors: Include embedding vectors in output

    Examples:
      index-cli sample                    # 5 random samples
      index-cli sample -n 10              # 10 random samples
      index-cli sample -c blog            # Random blog samples only
      index-cli sample --vectors          # Include embedding vectors
    """
    rprint(f'[blue]🎲 Getting {count} random samples...[/blue]')

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task('Sampling data...', total=None)

        try:
            pipeline = get_pipeline()

            if not pipeline.content_table:
                rprint('[red]❌ No database table found. Run indexing first.[/red]')
                raise typer.Exit(1)

            # Get total count for random sampling
            total_rows = pipeline.content_table.count_rows()

            if total_rows == 0:
                rprint('[yellow]No data found in database.[/yellow]')
                return

            # Build query with random sampling
            query = pipeline.content_table.search()

            if category:
                query = query.where(f"category = '{category}'")

            # Get more than needed and sample randomly
            sample_size = min(count * 3, total_rows)
            results = query.limit(sample_size).to_list()

            # Randomly sample from results
            import random

            random.shuffle(results)
            samples = results[:count]

            progress.update(task, completed=True)

            if not samples:
                rprint('[yellow]No samples found with the specified filters.[/yellow]')
                return

            rprint(f'[green]Found {len(samples)} random samples:[/green]\n')

            for i, sample in enumerate(samples, 1):
                rprint(f'[bold cyan]Sample {i}:[/bold cyan]')
                rprint(f'[bold]Title:[/bold] {sample.get("title", "N/A")}')
                rprint(f'[bold]Category:[/bold] {sample.get("category", "N/A")}')
                rprint(f'[bold]Post:[/bold] {sample.get("post_slug", "N/A")}')
                rprint(f'[bold]Chunk:[/bold] {sample.get("chunk_index", "N/A")}')
                rprint(f'[bold]Words:[/bold] {sample.get("word_count", "N/A")}')

                content = sample.get('content', '')
                if len(content) > 200:
                    content = content[:197] + '...'
                rprint(f'[bold]Content:[/bold] {content}')

                if show_vectors:
                    vector = sample.get('vector', [])
                    if vector:
                        vector_preview = (
                            vector[:5] + ['...'] if len(vector) > 5 else vector
                        )
                        rprint(
                            f'[bold]Vector:[/bold] {vector_preview} [dim](dim: {len(vector)})[/dim]'
                        )

                rprint('')  # Empty line between samples

        except Exception as e:
            progress.update(task, completed=True)
            rprint(f'[red]❌ Failed to sample data: {e}[/red]')
            raise typer.Exit(1)


@app.command('inspect')
def inspect_post(
    slug: str = typer.Argument(..., help='Post slug to inspect'),
    category: Optional[str] = typer.Option(
        None, '--category', '-c', help='Post category (auto-detected if not provided)'
    ),
    show_vectors: bool = typer.Option(
        False, '--vectors', help='Show embedding vectors'
    ),
    show_similarities: bool = typer.Option(
        False, '--similarities', help='Show similarities between chunks'
    ),
):
    """
    🔍 Deep dive inspection of a specific post's indexed data.

    View all chunks, embeddings, and metadata for a specific blog post.
    Useful for debugging indexing issues and understanding how content was processed.

    Options:
    • --category: Specify post category (auto-detected if not provided)
    • --vectors: Include embedding vectors in output
    • --similarities: Show similarity scores between chunks

    Examples:
      index-cli inspect "my-post-slug"                    # Basic inspection
      index-cli inspect "my-post" -c blog                 # With category
      index-cli inspect "my-post" --vectors               # Include vectors
      index-cli inspect "my-post" --similarities          # Show chunk similarities
    """
    rprint(f'[blue]🔍 Inspecting post: {slug}[/blue]')

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task('Loading post data...', total=None)

        try:
            pipeline = get_pipeline()

            if not pipeline.content_table:
                rprint('[red]❌ No database table found. Run indexing first.[/red]')
                raise typer.Exit(1)

            # Build query
            query = pipeline.content_table.search()

            if category:
                query = query.where(f"post_slug = '{slug}' AND category = '{category}'")
            else:
                query = query.where(f"post_slug = '{slug}'")

            chunks = query.to_list()
            progress.update(task, completed=True)

            if not chunks:
                rprint(f'[yellow]No data found for post: {slug}[/yellow]')
                if not category:
                    rprint('[dim]Try specifying --category if you know it[/dim]')
                return

            # Sort chunks by index
            chunks.sort(key=lambda x: x.get('chunk_index', 0))

            # Post summary
            first_chunk = chunks[0]
            rprint(f'[green]Found {len(chunks)} chunks for post: {slug}[/green]\n')

            # Summary table
            summary_table = Table(title='Post Summary')
            summary_table.add_column('Property', style='cyan')
            summary_table.add_column('Value', style='green')

            summary_table.add_row('Title', first_chunk.get('title', 'N/A'))
            summary_table.add_row('Category', first_chunk.get('category', 'N/A'))
            summary_table.add_row('Total Chunks', str(len(chunks)))
            summary_table.add_row(
                'Total Words', str(sum(c.get('word_count', 0) for c in chunks))
            )
            summary_table.add_row('Model Used', first_chunk.get('model_name', 'N/A'))
            summary_table.add_row(
                'Vector Dimension', str(first_chunk.get('vector_dim', 'N/A'))
            )

            console.print(summary_table)
            rprint('')

            # Chunks details
            for i, chunk in enumerate(chunks):
                rprint(
                    f'[bold cyan]Chunk {i + 1} (Index: {chunk.get("chunk_index", "N/A")}):[/bold cyan]'
                )
                rprint(f'[bold]Words:[/bold] {chunk.get("word_count", "N/A")}')
                rprint(f'[bold]Characters:[/bold] {len(chunk.get("content", ""))}')

                if chunk.get('section_title'):
                    rprint(f'[bold]Section:[/bold] {chunk.get("section_title")}')

                content = chunk.get('content', '')
                if len(content) > 300:
                    content = content[:297] + '...'
                rprint(f'[bold]Content:[/bold] {content}')

                if show_vectors:
                    vector = chunk.get('vector', [])
                    if vector:
                        vector_preview = (
                            vector[:10] + ['...'] if len(vector) > 10 else vector
                        )
                        rprint(f'[bold]Vector:[/bold] {vector_preview}')

                rprint('')

            # Calculate similarities if requested
            if show_similarities and len(chunks) > 1:
                rprint('[blue]📊 Chunk Similarities:[/blue]')

                import numpy as np

                vectors = []
                for chunk in chunks:
                    vector = chunk.get('vector', [])
                    if vector:
                        vectors.append(vector)

                if len(vectors) > 1:
                    similarities_table = Table(title='Chunk Similarity Matrix')
                    similarities_table.add_column('Chunk', style='cyan')

                    for i in range(len(vectors)):
                        similarities_table.add_column(f'C{i + 1}', style='green')

                    for i, vec1 in enumerate(vectors):
                        row = [f'Chunk {i + 1}']
                        for j, vec2 in enumerate(vectors):
                            if i == j:
                                sim = 1.0
                            else:
                                # Calculate cosine similarity
                                sim = np.dot(vec1, vec2) / (
                                    np.linalg.norm(vec1) * np.linalg.norm(vec2)
                                )
                            row.append(f'{sim:.3f}')
                        similarities_table.add_row(*row)

                    console.print(similarities_table)
                else:
                    rprint(
                        '[yellow]Not enough vectors for similarity calculation[/yellow]'
                    )

        except Exception as e:
            progress.update(task, completed=True)
            rprint(f'[red]❌ Failed to inspect post: {e}[/red]')
            raise typer.Exit(1)


@app.command('config')
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
        rprint(f'[red]❌ Failed to load config: {e}[/red]')
        raise typer.Exit(1)


if __name__ == '__main__':
    app()
