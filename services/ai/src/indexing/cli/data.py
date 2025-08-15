"""Data viewing and exploration commands."""

import random
from typing import Optional

import numpy as np
from rich import print as rprint
from rich.table import Table

from .utils import console, create_progress, get_pipeline, handle_error


def browse_data(
    limit: int = 20,
    category: Optional[str] = None,
    post: Optional[str] = None,
    columns: str = 'title,category,post_slug,content',
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

    with create_progress() as progress:
        task = progress.add_task('Loading data...', total=None)

        try:
            pipeline = get_pipeline()

            if not pipeline.content_table:
                rprint('[red]❌ No database table found. Run indexing first.[/red]')
                return

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
            handle_error('Browse data', e)


def sample_data(
    count: int = 5,
    category: Optional[str] = None,
    show_vectors: bool = False,
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

    with create_progress() as progress:
        task = progress.add_task('Sampling data...', total=None)

        try:
            pipeline = get_pipeline()

            if not pipeline.content_table:
                rprint('[red]❌ No database table found. Run indexing first.[/red]')
                return

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
                        vector_dim = len(vector)
                        rprint(
                            f'[bold]Vector:[/bold] {vector_preview} '
                            f'[dim](dim: {vector_dim})[/dim]'
                        )

                rprint('')  # Empty line between samples

        except Exception as e:
            progress.update(task, completed=True)
            handle_error('Sample data', e)


def inspect_post(
    slug: str,
    category: Optional[str] = None,
    show_vectors: bool = False,
    show_similarities: bool = False,
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

    with create_progress() as progress:
        task = progress.add_task('Loading post data...', total=None)

        try:
            pipeline = get_pipeline()

            if not pipeline.content_table:
                rprint('[red]❌ No database table found. Run indexing first.[/red]')
                return

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
            total_words = sum(c.get('word_count', 0) for c in chunks)
            summary_table.add_row('Total Words', str(total_words))
            summary_table.add_row('Model Used', first_chunk.get('model_name', 'N/A'))
            vector_dim = first_chunk.get('vector_dim', 'N/A')
            summary_table.add_row('Vector Dimension', str(vector_dim))

            console.print(summary_table)
            rprint('')

            # Chunks details
            for i, chunk in enumerate(chunks):
                chunk_index = chunk.get('chunk_index', 'N/A')
                rprint(f'[bold cyan]Chunk {i + 1} (Index: {chunk_index}):[/bold cyan]')
                rprint(f'[bold]Words:[/bold] {chunk.get("word_count", "N/A")}')
                content_len = len(chunk.get('content', ''))
                rprint(f'[bold]Characters:[/bold] {content_len}')

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
            handle_error('Inspect post', e)
