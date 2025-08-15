"""
Blog Content Indexing CLI

A modern command-line interface for the blog content indexing pipeline.
Uses typer for a friendly CLI experience with rich output formatting.
"""

from typing import Optional

import typer

from .cli.core import clear_index, index_content, test_pipeline
from .cli.data import browse_data, inspect_post, sample_data
from .cli.search import search_content, show_config, show_stats

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


@app.command('test')
def test_cmd():
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
    test_pipeline()


@app.command('index')
def index_cmd(
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
    index_content(category=category, slug=slug, force=force)


@app.command('stats')
def stats_cmd():
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
    show_stats()


@app.command('clear')
def clear_cmd(
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
    clear_index(category=category, confirm=confirm)


@app.command('search')
def search_cmd(
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
    search_content(
        query=query,
        limit=limit,
        category=category,
        threshold=threshold,
        mode=mode,
        case_sensitive=case_sensitive,
    )


@app.command('browse')
def browse_cmd(
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
    browse_data(limit=limit, category=category, post=post, columns=columns)


@app.command('sample')
def sample_cmd(
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
    sample_data(count=count, category=category, show_vectors=show_vectors)


@app.command('inspect')
def inspect_cmd(
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
    inspect_post(
        slug=slug,
        category=category,
        show_vectors=show_vectors,
        show_similarities=show_similarities,
    )


@app.command('config')
def config_cmd():
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
    show_config()


if __name__ == '__main__':
    app()
