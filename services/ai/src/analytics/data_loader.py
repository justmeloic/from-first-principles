"""
Data loader for analytics dashboard.

Loads and processes data from various sources including content files,
LanceDB tables, and log files for comprehensive analysis.
"""

import os
import re
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import lancedb
import pandas as pd

@dataclass
class ContentStats:
    """Statistics about content data."""
    total_posts: int
    categories: Dict[str, int]
    tags: Dict[str, int]
    authors: Dict[str, int]
    avg_reading_time: float
    avg_word_count: float
    featured_posts: int
    difficulty_levels: Dict[str, int]
    date_range: Tuple[str, str]


class DataLoader:
    """Loads and processes data for analytics dashboard."""

    def __init__(self, data_dir: str = "data"):
        """Initialize data loader with data directory path."""
        self.data_dir = Path(data_dir)
        self.content_dir = self.data_dir / "content"
        self.lancedb_dir = self.data_dir / "lancedb"
        self.logs_dir = Path("logs")

    def load_content_metadata(self) -> pd.DataFrame:
        """Load all blog post metadata into a DataFrame."""
        metadata_list = []

        # Process blog and engineering directories
        for category in ["blog", "engineering"]:
            category_dir = self.content_dir / category
            if not category_dir.exists():
                continue

            for post_dir in category_dir.iterdir():
                if not post_dir.is_dir():
                    continue

                metadata_file = post_dir / "metadata.yaml"
                if not metadata_file.exists():
                    continue

                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = yaml.safe_load(f)

                    # Flatten nested dictionaries for easier analysis
                    flattened = self._flatten_metadata(metadata)
                    flattened['post_directory'] = str(post_dir)
                    flattened['category'] = category

                    metadata_list.append(flattened)

                except Exception as e:
                    print(f"Error loading {metadata_file}: {e}")
                    continue

        if not metadata_list:
            return pd.DataFrame()

        df = pd.DataFrame(metadata_list)

        # Convert date columns
        date_cols = ['publish_date', 'last_modified']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """Flatten nested metadata dictionary."""
        flattened = {}

        for key, value in metadata.items():
            if isinstance(value, dict):
                # Handle nested dictionaries
                for sub_key, sub_value in value.items():
                    flattened[f"{key}_{sub_key}"] = sub_value
            elif isinstance(value, list):
                # Convert lists to comma-separated strings for some fields
                if key == 'tags':
                    flattened[key] = value
                    flattened[f'{key}_str'] = ', '.join(map(str, value))
                else:
                    flattened[key] = value
            else:
                flattened[key] = value

        return flattened

    def load_lancedb_data(self) -> Optional[pd.DataFrame]:
        """Load data from LanceDB tables."""
        try:
            db = lancedb.connect(str(self.lancedb_dir))

            # Check for blog_content table
            if "blog_content" in db.table_names():
                table = db.open_table("blog_content")
                df = table.to_pandas()
                return df
            else:
                print("No blog_content table found in LanceDB")
                return None

        except Exception as e:
            print(f"Error loading LanceDB data: {e}")
            return None

    def load_search_logs(self) -> Optional[pd.DataFrame]:
        """Load and parse search logs."""
        try:
            log_file = self.logs_dir / "app.log"
            if not log_file.exists():
                return None

            search_entries = []

            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'search' in line.lower() or 'query' in line.lower():
                        # Parse log entry (adjust pattern based on your log format)
                        entry = self._parse_log_entry(line)
                        if entry:
                            search_entries.append(entry)

            if search_entries:
                return pd.DataFrame(search_entries)
            else:
                return None

        except Exception as e:
            print(f"Error loading search logs: {e}")
            return None

    def _parse_log_entry(self, line: str) -> Optional[Dict]:
        """Parse a single log entry."""
        # This is a basic parser - adjust based on your log format
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        timestamp_match = re.search(timestamp_pattern, line)

        if timestamp_match:
            return {
                'timestamp': pd.to_datetime(timestamp_match.group()),
                'log_entry': line.strip(),
                'level': self._extract_log_level(line),
                'message': line[timestamp_match.end():].strip()
            }
        return None

    def _extract_log_level(self, line: str) -> str:
        """Extract log level from log line."""
        levels = ['ERROR', 'WARN', 'INFO', 'DEBUG']
        for level in levels:
            if level in line.upper():
                return level
        return 'UNKNOWN'

    def get_content_stats(self, df: pd.DataFrame) -> ContentStats:
        """Generate content statistics."""
        if df.empty:
            return ContentStats(0, {}, {}, {}, 0, 0, 0, {}, ("", ""))

        # Category distribution
        categories = df['category'].value_counts().to_dict()

        # Tag analysis
        all_tags = []
        for tags in df['tags'].dropna():
            if isinstance(tags, list):
                all_tags.extend(tags)
        tag_counts = pd.Series(all_tags).value_counts().to_dict()

        # Author distribution
        authors = df['author'].value_counts().to_dict()

        # Difficulty levels
        difficulty_levels = df['content_difficulty_level'].value_counts().to_dict()

        # Date range
        dates = df['publish_date'].dropna()
        if len(dates) > 0:
            date_range = (str(dates.min().date()), str(dates.max().date()))
        else:
            date_range = ("", "")

        return ContentStats(
            total_posts=len(df),
            categories=categories,
            tags=tag_counts,
            authors=authors,
            avg_reading_time=(
                df['reading_time'].mean() if 'reading_time' in df.columns else 0
            ),
            avg_word_count=(
                df['word_count'].mean() if 'word_count' in df.columns else 0
            ),
            featured_posts=df['featured'].sum() if 'featured' in df.columns else 0,
            difficulty_levels=difficulty_levels,
            date_range=date_range
        )

    def load_embedding_stats(self) -> Optional[Dict]:
        """Load embedding statistics from LanceDB."""
        try:
            lancedb_data = self.load_lancedb_data()
            if lancedb_data is None:
                return None

            stats = {}

            # Check if vector column exists
            if 'vector' in lancedb_data.columns:
                # Vector dimension analysis
                first_vector = lancedb_data['vector'].iloc[0]
                if isinstance(first_vector, (list, tuple)):
                    stats['vector_dimension'] = len(first_vector)
                else:
                    stats['vector_dimension'] = 'Unknown'

                stats['total_embeddings'] = len(lancedb_data)

                # Check for chunk information
                if 'chunk_id' in lancedb_data.columns:
                    stats['total_chunks'] = lancedb_data['chunk_id'].nunique()

                # Check for post information
                if 'post_slug' in lancedb_data.columns:
                    stats['embedded_posts'] = lancedb_data['post_slug'].nunique()

            return stats

        except Exception as e:
            print(f"Error loading embedding stats: {e}")
            return None

    def get_file_system_stats(self) -> Dict:
        """Get file system statistics for content directory."""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'file_types': {},
            'directory_structure': {}
        }

        try:
            for root, dirs, files in os.walk(self.content_dir):
                for file in files:
                    file_path = Path(root) / file
                    stats['total_files'] += 1

                    # File size
                    try:
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        stats['total_size_mb'] += size_mb
                    except Exception:
                        pass

                    # File extension
                    ext = file_path.suffix.lower()
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1

                    # Directory structure
                    rel_path = file_path.relative_to(self.content_dir)
                    parent_dir = str(rel_path.parent)
                    if parent_dir not in stats['directory_structure']:
                        stats['directory_structure'][parent_dir] = 0
                    stats['directory_structure'][parent_dir] += 1

            stats['total_size_mb'] = round(stats['total_size_mb'], 2)

        except Exception as e:
            print(f"Error getting file system stats: {e}")

        return stats
