"""
Main pipeline builder for the blog indexing system.

This module orchestrates the entire indexing process, coordinating
content loading, text processing, embedding generation, and database storage.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import lancedb

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

from .config import get_config
from .document import BlogPost, ContentChunk, EmbeddingVector, IndexingResult
from .embedder import EmbeddingGenerator
from .loader import ContentLoader
from .utils.text_processing import TextProcessor


class IndexingPipeline:
    """Main pipeline for indexing blog content."""

    def __init__(self, config=None):
        """Initialize the indexing pipeline."""
        self.config = config or get_config()

        # Initialize components
        self.loader = ContentLoader(self.config)
        self.text_processor = TextProcessor(self.config)
        self.embedder = EmbeddingGenerator(self.config)

        # Database connection
        self.db = None
        self.content_table = None

        # Results tracking
        self.current_result = None

        # Initialize database
        self._initialize_database()

    def _initialize_database(self):
        """Initialize LanceDB database and tables."""
        if not LANCEDB_AVAILABLE:
            print('Warning: LanceDB not available. Database features disabled.')
            return

        try:
            # Create database directory if it doesn't exist
            db_path = Path(self.config.database.db_path)
            db_path.mkdir(parents=True, exist_ok=True)

            # Connect to database
            self.db = lancedb.connect(str(db_path))
            print(f'Connected to LanceDB at: {db_path}')

            # Initialize tables if they don't exist
            self._ensure_tables_exist()

        except Exception as e:
            print(f'Failed to initialize database: {e}')
            self.db = None

    def _ensure_tables_exist(self):
        """Ensure required database tables exist."""
        if not self.db:
            return

        try:
            # Check if content table exists
            table_names = self.db.table_names()

            if self.config.database.table_name not in table_names:
                # Create content table with correct schema
                self._recreate_table_with_correct_schema()
            else:
                self.content_table = self.db.open_table(self.config.database.table_name)
                print(
                    f'Opened existing content table: {self.config.database.table_name}'
                )

        except Exception as e:
            print(f'Error setting up database tables: {e}')
            # If there's an error, try recreating the table
            try:
                self._recreate_table_with_correct_schema()
            except Exception as recreate_error:
                print(f'Failed to recreate table: {recreate_error}')

    def _recreate_table_with_correct_schema(self) -> None:
        """Recreate the table with the correct schema for current data format."""
        try:
            if not LANCEDB_AVAILABLE:
                print('❌ LanceDB not available - cannot recreate table')
                return

            print('🔄 Recreating table with correct schema...')

            # Drop existing table if it exists
            try:
                self.db.drop_table(self.config.database.table_name)
                print(f'🗑️  Dropped existing table: {self.config.database.table_name}')
            except Exception:
                print(f'⚠️  Table {self.config.database.table_name} did not exist')

            # Create sample data with correct schema
            embedding_dim = self.embedder.get_model_info()['embedding_dimension']

            sample_data = [
                {
                    'chunk_id': 'sample_chunk_001',
                    'post_slug': 'sample-post',
                    'category': 'blog',
                    'title': 'Sample Post',
                    'content': 'This is sample content for schema creation.',
                    'chunk_index': 0,
                    'start_char': 0,
                    'end_char': 45,
                    'word_count': 8,
                    'section_title': '',
                    'vector': [0.0] * embedding_dim,
                    'vector_dim': embedding_dim,
                    'model_name': 'all-MiniLM-L6-v2',
                    'model_version': '1.0',
                    'created_at': datetime.now(),
                    'processing_time_ms': 0.0,
                    'vector_hash': 'sample_hash',
                }
            ]

            # Create new table with correct schema
            self.content_table = self.db.create_table(
                self.config.database.table_name, sample_data
            )

            # Remove sample data
            self.content_table.delete("chunk_id = 'sample_chunk_001'")

            print(
                f'✅ Created new table with correct schema: '
                f'{self.config.database.table_name}'
            )

        except Exception as e:
            print(f'❌ Error recreating table: {e}')
            raise

    def index_all(self, force_reindex: bool = False) -> IndexingResult:
        """Index all blog posts."""
        print('Starting content indexing...')
        # Implementation here...

    def _store_embeddings(
        self,
        post: BlogPost,
        chunks: List[ContentChunk],
        embedding_vectors: List[EmbeddingVector],
    ) -> None:
        """Store embeddings in the database with comprehensive error handling."""
        if self.content_table is None:
            print('❌ Database table not available for storage')
            return

        if not chunks or not embedding_vectors:
            print('❌ No chunks or embeddings to store')
            return

        if len(chunks) != len(embedding_vectors):
            print(
                f'❌ Chunk count ({len(chunks)}) != '
                f'embedding count ({len(embedding_vectors)})'
            )
            return

        try:
            print(
                f'📝 Preparing to store {len(embedding_vectors)} embeddings '
                f'for post: {post.metadata.slug}'
            )

            # Prepare data for batch insert with validation
            data_to_insert = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embedding_vectors)):
                try:
                    # Validate required fields
                    if not chunk.content or not chunk.content.strip():
                        print(f'⚠️  Warning: Empty content for chunk {i}, skipping')
                        continue

                    if not embedding.vector or len(embedding.vector) == 0:
                        print(f'⚠️  Warning: Empty vector for chunk {i}, skipping')
                        continue

                    record = {
                        'chunk_id': str(embedding.chunk_id or f'chunk_{i}'),
                        'post_slug': str(post.metadata.slug or 'unknown'),
                        'category': str(post.metadata.category or 'uncategorized'),
                        'title': str(post.metadata.title or 'Untitled'),
                        'content': str(chunk.content).strip(),
                        'chunk_index': int(chunk.chunk_index or i),
                        'start_char': int(chunk.start_char or 0),
                        'end_char': int(chunk.end_char or len(chunk.content)),
                        'word_count': int(
                            chunk.word_count or len(chunk.content.split())
                        ),
                        'section_title': str(chunk.section_title or ''),
                        'vector': list(embedding.vector),  # Ensure it's a list
                        'vector_dim': int(
                            embedding.vector_dim or len(embedding.vector)
                        ),
                        'model_name': str(embedding.model_name or 'unknown'),
                        'model_version': str(embedding.model_version or ''),
                        'created_at': embedding.created_at,
                        'processing_time_ms': float(
                            embedding.processing_time_ms or 0.0
                        ),
                        'vector_hash': str(embedding.vector_hash or ''),
                    }

                    # Validate vector dimensions
                    if len(record['vector']) != record['vector_dim']:
                        print(f'⚠️  Warning: Vector dimension mismatch for chunk {i}')
                        record['vector_dim'] = len(record['vector'])

                    data_to_insert.append(record)

                except Exception as chunk_error:
                    print(f'❌ Error preparing chunk {i}: {chunk_error}')
                    continue

            if not data_to_insert:
                print('❌ No valid data to insert after validation')
                return

            print(
                f'💾 Inserting {len(data_to_insert)} validated records into database...'
            )

            # Insert data with error handling
            self.content_table.add(data_to_insert)
            print(
                f'✅ Successfully stored {len(data_to_insert)} embeddings '
                f'for {post.metadata.slug}'
            )

        except Exception as e:
            print(f'❌ Error storing embeddings for {post.metadata.slug}: {e}')
            print(f'❌ Error type: {type(e).__name__}')

            # Try to provide more specific error information
            if 'schema' in str(e).lower():
                print(
                    '❌ Schema error detected - table structure may need '
                    'to be recreated'
                )
            elif 'cast' in str(e).lower():
                print('❌ Data type casting error - check field types')
            elif 'null' in str(e).lower():
                print('❌ Null value error - check for missing required fields')

            # Re-raise for debugging
            raise

    def _start_indexing_operation(self) -> IndexingResult:
        """Start a new indexing operation and return result tracker."""
        operation_id = str(uuid.uuid4())
        result = IndexingResult(operation_id=operation_id, started_at=datetime.utcnow())
        self.current_result = result
        return result

    def _finish_indexing_operation(self, status: str = 'completed'):
        """Finish the current indexing operation."""
        if self.current_result:
            self.current_result.completed_at = datetime.utcnow()
            self.current_result.status = status

    def quick_test(self) -> Dict[str, Any]:
        """Quick test of the pipeline configuration and dependencies."""
        try:
            # Test embedding generation
            embedding_test = self.embedder.test_embedding()

            if not embedding_test['success']:
                return {
                    'success': False,
                    'error': 'Embedding test failed',
                    'details': embedding_test,
                }

            # Test content loading
            posts = self.loader.load_all_posts()

            if not posts:
                return {'success': False, 'error': 'No posts found for testing'}

            # Test processing with first post
            test_post = posts[0]
            chunks = self.text_processor.create_chunks(
                test_post.processed_content,
                test_post.metadata.slug,
                test_post.metadata.category,
            )

            return {
                'success': True,
                'embedding_test': embedding_test,
                'posts_found': len(posts),
                'test_post': {
                    'slug': test_post.metadata.slug,
                    'content_length': len(test_post.processed_content),
                    'chunks_created': len(chunks),
                },
                'database_available': self.db is not None,
                'config': {
                    'embedding_model': self.config.embedding.model_name,
                    'chunk_size': self.config.chunking.chunk_size,
                },
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def index_all_content(
        self, category_filter: Optional[str] = None, force_reindex: bool = False
    ) -> IndexingResult:
        """Index all content with optional category filtering."""
        result = self._start_indexing_operation()

        try:
            print('Starting content indexing...')
            if category_filter:
                print(f'Filtering by category: {category_filter}')

            # Load posts
            posts = self.loader.load_all_posts()

            # Filter by category if specified
            if category_filter:
                posts = [p for p in posts if p.metadata.category == category_filter]

            print(f'Found {len(posts)} posts to process')

            if not posts:
                result.warnings.append('No posts found to index')
                self._finish_indexing_operation()
                return result

            # Process posts
            for post in posts:
                try:
                    print(f'Processing: {post.metadata.category}/{post.metadata.slug}')

                    # Create chunks and embeddings
                    chunks = self.text_processor.create_chunks(
                        post.processed_content,
                        post.metadata.slug,
                        post.metadata.category,
                    )

                    if chunks:
                        embedding_vectors = self.embedder.create_embedding_vectors(
                            chunks
                        )

                        # Store embeddings in database
                        if embedding_vectors and self.content_table is not None:
                            self._store_embeddings(post, chunks, embedding_vectors)

                        result.chunks_created += len(chunks)
                        result.embeddings_generated += len(embedding_vectors)

                    result.posts_processed += 1

                except Exception as e:
                    print(f'Error processing post {post.metadata.slug}: {e}')
                    result.posts_skipped += 1
                    result.errors.append(str(e))

            result.posts_updated = result.posts_processed - result.posts_skipped

            print('Indexing completed:')
            print(f'  - Posts processed: {result.posts_processed}')
            print(f'  - Posts updated: {result.posts_updated}')
            print(f'  - Posts skipped: {result.posts_skipped}')
            print(f'  - Chunks created: {result.chunks_created}')
            print(f'  - Embeddings generated: {result.embeddings_generated}')

            self._finish_indexing_operation()

        except Exception as e:
            error_msg = f'Fatal error during indexing: {e}'
            print(error_msg)
            result.errors.append(error_msg)
            self._finish_indexing_operation('failed')

        return result

    def index_single_post(self, category: str, slug: str) -> Optional[IndexingResult]:
        """Index a single blog post."""
        result = self._start_indexing_operation()

        try:
            print(f'Indexing single post: {category}/{slug}')

            # Load the specific post
            post = self.loader.get_post_by_slug(category, slug)

            if not post:
                error_msg = f'Post not found: {category}/{slug}'
                result.errors.append(error_msg)
                self._finish_indexing_operation('failed')
                return result

            # Process the post
            chunks = self.text_processor.create_chunks(
                post.processed_content,
                post.metadata.slug,
                post.metadata.category,
            )

            if chunks:
                embedding_vectors = self.embedder.create_embedding_vectors(chunks)
                result.chunks_created = len(chunks)
                result.embeddings_generated = len(embedding_vectors)

            result.posts_processed = 1
            result.posts_updated = 1

            print(f'Successfully indexed {category}/{slug}')
            self._finish_indexing_operation()

        except Exception as e:
            error_msg = f'Error indexing post {category}/{slug}: {e}'
            print(error_msg)
            result.errors.append(error_msg)
            self._finish_indexing_operation('failed')

        return result

    def search(
        self,
        query: str,
        limit: int = 10,
        category_filter: Optional[str] = None,
        similarity_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search indexed content using semantic similarity."""
        if self.content_table is None:
            print('Database not available for search')
            return []

        try:
            # Generate embedding for the query
            query_embedding = self.embedder.generate_embedding(query)

            # Build search query
            search_query = self.content_table.search(query_embedding).limit(limit)

            # Add category filter if specified
            if category_filter:
                search_query = search_query.where(f"category = '{category_filter}'")

            # Execute search
            results = search_query.to_list()

            # Format results
            formatted_results = []
            for result in results:
                # LanceDB returns squared Euclidean distance
                distance = result.get('_distance', float('inf'))

                # Convert distance to similarity score (0-1, higher is better)
                # For squared Euclidean distance, smaller is more similar
                # We use a simple inverse relationship with max distance cap
                max_distance = 4.0  # Cap for normalization
                similarity_score = max(0.0, 1.0 - (distance / max_distance))

                # Apply similarity threshold (default 0.5 for balanced results)
                if similarity_score >= similarity_threshold:
                    formatted_results.append(
                        {
                            'title': result.get('title', ''),
                            'category': result.get('category', ''),
                            'slug': result.get('post_slug', ''),
                            'content': result.get('content', ''),
                            'excerpt': result.get('content', '')[:200] + '...',
                            'score': similarity_score,
                            'distance': distance,
                            'publish_date': result.get('publish_date', ''),
                            'tags': result.get('tags', []),
                            'url': result.get('url', ''),
                        }
                    )

            return formatted_results

        except Exception as e:
            print(f'Error during search: {e}')
            return []

    def keyword_search(
        self,
        query: str,
        limit: int = 10,
        category_filter: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search indexed content using keyword/text matching."""
        if self.content_table is None:
            print('Database not available for search')
            return []

        try:
            # Prepare query terms
            query_terms = query.lower().split() if not case_sensitive else query.split()

            # Build SQL-like search conditions
            search_conditions = []
            for term in query_terms:
                if case_sensitive:
                    search_conditions.append(f"content LIKE '%{term}%'")
                else:
                    search_conditions.append(f"LOWER(content) LIKE '%{term.lower()}%'")

            # Combine conditions with OR (find content with any of the terms)
            where_clause = ' OR '.join(search_conditions)

            # Add category filter if specified
            if category_filter:
                where_clause = f"({where_clause}) AND category = '{category_filter}'"

            # Execute search
            search_query = (
                self.content_table.search().where(where_clause).limit(limit * 2)
            )  # Get more to rank
            results = search_query.to_list()

            # Calculate relevance scores based on term frequency and position
            scored_results = []
            for result in results:
                content = (
                    result.get('content', '').lower()
                    if not case_sensitive
                    else result.get('content', '')
                )
                title = (
                    result.get('title', '').lower()
                    if not case_sensitive
                    else result.get('title', '')
                )

                score = 0.0
                term_matches = 0

                for term in query_terms:
                    search_term = term.lower() if not case_sensitive else term

                    # Count occurrences in content
                    content_matches = content.count(search_term)
                    title_matches = title.count(search_term)

                    if content_matches > 0:
                        term_matches += 1
                        score += content_matches * 0.1  # Base score for content matches

                        # Bonus for early appearance
                        first_pos = content.find(search_term)
                        if first_pos < 100:  # Within first 100 characters
                            score += 0.3

                    if title_matches > 0:
                        term_matches += 1
                        score += title_matches * 0.5  # Higher weight for title matches

                # Bonus for matching multiple terms
                if len(query_terms) > 1:
                    score += (term_matches / len(query_terms)) * 0.5

                if score > 0:
                    scored_results.append(
                        {
                            'title': result.get('title', ''),
                            'category': result.get('category', ''),
                            'slug': result.get('post_slug', ''),
                            'content': result.get('content', ''),
                            'excerpt': result.get('content', '')[:200] + '...',
                            'score': min(score, 1.0),  # Cap at 1.0
                            'term_matches': term_matches,
                            'publish_date': result.get('publish_date', ''),
                            'tags': result.get('tags', []),
                            'url': result.get('url', ''),
                        }
                    )

            # Sort by score (descending) and limit results
            scored_results.sort(key=lambda x: x['score'], reverse=True)
            return scored_results[:limit]

        except Exception as e:
            print(f'Error during keyword search: {e}')
            return []

    def search_unified(
        self,
        query: str,
        mode: str = 'semantic',
        limit: int = 10,
        category_filter: Optional[str] = None,
        similarity_threshold: float = 0.5,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Unified search interface that can switch between semantic and keyword search.

        Args:
            query: Search query string
            mode: 'semantic' for vector similarity search, 'keyword' for text matching
            limit: Maximum number of results to return
            category_filter: Optional category to filter by
            similarity_threshold: Minimum similarity score for semantic search
            case_sensitive: Whether keyword search should be case sensitive
        """
        if mode.lower() == 'keyword':
            return self.keyword_search(
                query=query,
                limit=limit,
                category_filter=category_filter,
                case_sensitive=case_sensitive,
            )
        else:  # Default to semantic search
            return self.search(
                query=query,
                limit=limit,
                category_filter=category_filter,
                similarity_threshold=similarity_threshold,
            )

    def get_indexing_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed content."""
        stats = {
            'database_available': self.db is not None,
            'categories': {},
            'database': {},
            'embedding_info': self.embedder.get_model_info(),
        }

        if self.content_table:
            try:
                # Get total count
                total_count = self.content_table.count_rows()
                stats['total_chunks'] = total_count

                # Get stats by category
                for category in ['blog', 'engineering']:
                    try:
                        # Count chunks in this category
                        chunks = (
                            self.content_table.search()
                            .where(f"category = '{category}'")
                            .to_list()
                        )

                        # Count unique posts
                        unique_slugs = set(
                            chunk.get('post_slug', '') for chunk in chunks
                        )
                        unique_posts = len(unique_slugs)

                        stats['categories'][category] = {
                            'posts': unique_posts,
                            'chunks': len(chunks),
                            'last_updated': max(
                                (chunk.get('created_at', '') for chunk in chunks),
                                default='Never',
                            ),
                        }
                    except Exception:
                        stats['categories'][category] = {
                            'posts': 0,
                            'chunks': 0,
                            'last_updated': 'Never',
                        }

                # Database info
                stats['database'] = {
                    'location': str(self.config.database.db_path),
                    'table_name': self.config.database.table_name,
                    'size': 'Unknown',
                }

            except Exception as e:
                stats['error'] = f'Error getting database stats: {e}'

        return stats

    def clear_index(self, category: Optional[str] = None):
        """Clear the index (optionally for a specific category)."""
        if not self.content_table:
            print('No database connection available')
            return

        try:
            if category:
                # Delete specific category
                self.content_table.delete(f"category = '{category}'")
                print(f'Cleared index for category: {category}')
            else:
                # Clear entire table
                self.content_table.delete('chunk_id IS NOT NULL')
                print('Cleared entire index')

        except Exception as e:
            print(f'Error clearing index: {e}')
