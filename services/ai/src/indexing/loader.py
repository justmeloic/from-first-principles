"""
Content loader for the blog indexing pipeline.

This module handles loading and parsing content from the file system,
including Markdown files and YAML metadata.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional

import yaml

from .config import get_config
from .document import BlogPost, ContentMetadata


class ContentLoader:
    """Load and parse blog content from the file system."""

    def __init__(self, config=None):
        """Initialize the content loader."""
        self.config = config or get_config()
        self.content_root = Path(self.config.content.content_root)

        # Validate content root exists
        if not self.content_root.exists():
            raise ValueError(f'Content root does not exist: {self.content_root}')

    def discover_posts(self) -> Generator[Path, None, None]:
        """Discover all blog posts in the content directory."""
        for category in self.config.content.supported_categories:
            category_path = self.content_root / category

            if not category_path.exists():
                continue

            # Iterate through all post directories
            for post_dir in category_path.iterdir():
                if post_dir.is_dir():
                    # Check if it has required files
                    markdown_file = post_dir / self.config.content.markdown_file
                    metadata_file = post_dir / self.config.content.metadata_file

                    if markdown_file.exists() and metadata_file.exists():
                        yield post_dir

    def load_metadata(self, metadata_file: Path) -> ContentMetadata:
        """Load and validate metadata from YAML file."""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Remove the comment line if it exists
            if isinstance(data, dict):
                # Clean up any None values that might come from YAML parsing
                cleaned_data = {k: v for k, v in data.items() if v is not None}
                return ContentMetadata(**cleaned_data)
            else:
                raise ValueError('Metadata file does not contain valid YAML dictionary')

        except yaml.YAMLError as e:
            raise ValueError(f'Invalid YAML in metadata file: {e}')
        except Exception as e:
            raise ValueError(f'Error loading metadata: {e}')

    def load_markdown_content(self, markdown_file: Path) -> str:
        """Load raw markdown content from file."""
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f'Error loading markdown content: {e}')

    def process_markdown_to_text(self, markdown_content: str) -> str:
        """Convert markdown to plain text for indexing."""
        try:
            from markdown_it import MarkdownIt

            # Create markdown parser
            md = MarkdownIt()

            # Parse markdown to tokens
            tokens = md.parse(markdown_content)

            # Extract text content from tokens
            text_parts = []
            for token in tokens:
                if token.type == 'paragraph_open':
                    continue
                elif token.type == 'paragraph_close':
                    text_parts.append('\n\n')
                elif token.type == 'heading_open':
                    continue
                elif token.type == 'heading_close':
                    text_parts.append('\n\n')
                elif token.type == 'inline':
                    # Process inline content
                    if token.children:
                        for child in token.children:
                            if child.type == 'text':
                                text_parts.append(child.content)
                            elif child.type == 'link_open':
                                continue
                            elif child.type == 'link_close':
                                continue
                            elif hasattr(child, 'content'):
                                text_parts.append(child.content)
                    else:
                        text_parts.append(token.content)
                elif hasattr(token, 'content') and token.content:
                    text_parts.append(token.content)

            # Join and clean up text
            text = ''.join(text_parts)

            # Clean up extra whitespace
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                cleaned_line = line.strip()
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)

            return '\n'.join(cleaned_lines)

        except ImportError:
            # Fallback to simple text extraction if markdown_it is not available
            return self._simple_markdown_to_text(markdown_content)
        except Exception as e:
            raise ValueError(f'Error processing markdown: {e}')

    def _simple_markdown_to_text(self, markdown_content: str) -> str:
        """Simple fallback markdown to text conversion."""
        import re

        # Remove common markdown syntax
        text = markdown_content

        # Remove headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

        # Remove bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Remove list markers
        text = re.sub(r'^[\s]*[-*+]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)

        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = text.strip()

        return text

    def get_file_stats(self, file_path: Path) -> Dict:
        """Get file statistics."""
        stat = file_path.stat()
        return {
            'size_bytes': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
        }

    def load_post(self, post_dir: Path) -> BlogPost:
        """Load a complete blog post with metadata and content."""
        # Determine category from directory structure
        category = post_dir.parent.name

        # File paths
        markdown_file = post_dir / self.config.content.markdown_file
        metadata_file = post_dir / self.config.content.metadata_file

        # Load metadata
        metadata = self.load_metadata(metadata_file)

        # Validate category matches directory structure
        if metadata.category != category:
            raise ValueError(
                f"Metadata category '{metadata.category}' does not match "
                f"directory category '{category}'"
            )

        # Load and process content
        raw_content = self.load_markdown_content(markdown_file)
        processed_content = self.process_markdown_to_text(raw_content)

        # Validate content length
        if len(processed_content) < self.config.content.min_content_length:
            raise ValueError(
                f'Content too short: {len(processed_content)} characters '
                f'(minimum: {self.config.content.min_content_length})'
            )

        # Get file statistics
        file_stats = self.get_file_stats(markdown_file)

        # Create BlogPost object
        blog_post = BlogPost(
            directory_path=str(post_dir),
            markdown_file=str(markdown_file),
            metadata_file=str(metadata_file),
            metadata=metadata,
            raw_content=raw_content,
            processed_content=processed_content,
            file_size_bytes=file_stats['size_bytes'],
            file_modified_time=file_stats['modified_time'],
        )

        return blog_post

    def should_include_post(self, metadata: ContentMetadata) -> bool:
        """Determine if a post should be included in indexing."""
        # Skip drafts unless explicitly included
        if metadata.status == 'draft' and not self.config.content.include_drafts:
            return False

        # Skip archived posts
        if metadata.status == 'archived':
            return False

        return True

    def load_all_posts(self) -> List[BlogPost]:
        """Load all blog posts from the content directory."""
        posts = []
        errors = []

        for post_dir in self.discover_posts():
            try:
                # Load metadata first to check if we should include the post
                metadata_file = post_dir / self.config.content.metadata_file
                metadata = self.load_metadata(metadata_file)

                if not self.should_include_post(metadata):
                    continue

                # Load the full post
                post = self.load_post(post_dir)
                posts.append(post)

            except Exception as e:
                error_msg = f'Error loading post from {post_dir}: {e}'
                errors.append(error_msg)
                print(f'Warning: {error_msg}')

        if errors:
            print(f'Encountered {len(errors)} errors while loading posts')

        return posts

    def get_post_by_slug(self, category: str, slug: str) -> Optional[BlogPost]:
        """Load a specific post by category and slug."""
        post_dir = self.content_root / category / slug

        if not post_dir.exists():
            return None

        try:
            return self.load_post(post_dir)
        except Exception as e:
            print(f'Error loading post {category}/{slug}: {e}')
            return None

    def get_content_stats(self) -> Dict:
        """Get statistics about the content collection."""
        stats = {
            'total_posts': 0,
            'posts_by_category': {},
            'posts_by_status': {},
            'total_content_length': 0,
            'average_content_length': 0,
            'posts_with_errors': [],
        }

        for post_dir in self.discover_posts():
            try:
                metadata_file = post_dir / self.config.content.metadata_file
                metadata = self.load_metadata(metadata_file)

                stats['total_posts'] += 1

                # Count by category
                category = metadata.category
                stats['posts_by_category'][category] = (
                    stats['posts_by_category'].get(category, 0) + 1
                )

                # Count by status
                status = metadata.status
                stats['posts_by_status'][status] = (
                    stats['posts_by_status'].get(status, 0) + 1
                )

                # Content length (only for non-drafts to get realistic stats)
                if metadata.status == 'published':
                    post = self.load_post(post_dir)
                    content_length = len(post.processed_content)
                    stats['total_content_length'] += content_length

            except Exception as e:
                stats['posts_with_errors'].append(str(post_dir))

        # Calculate average
        published_count = stats['posts_by_status'].get('published', 0)
        if published_count > 0:
            stats['average_content_length'] = (
                stats['total_content_length'] / published_count
            )

        return stats
