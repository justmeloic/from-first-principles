"""
Text processing utilities for the blog indexing pipeline.

This module provides utilities for cleaning, chunking, and preprocessing text content.
"""

import re
from typing import List, Optional, Tuple

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..config import get_config
from ..document import ContentChunk


class TextProcessor:
    """Process and clean text content for indexing."""

    def __init__(self, config=None):
        """Initialize the text processor."""
        self.config = config or get_config()

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ''

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove extra line breaks but preserve paragraph structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Clean up common issues
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def extract_sections(self, text: str) -> List[Tuple[str, str]]:
        """Extract sections from text based on headers."""
        sections = []

        # Split by headers (### or more #)
        header_pattern = r'^(#{3,})\s+(.+)$'
        lines = text.split('\n')

        current_section = ''
        current_title = None

        for line in lines:
            header_match = re.match(header_pattern, line)

            if header_match:
                # Save previous section if it exists
                if current_title and current_section.strip():
                    sections.append((current_title, current_section.strip()))

                # Start new section
                current_title = header_match.group(2).strip()
                current_section = ''
            else:
                current_section += line + '\n'

        # Add the last section
        if current_title and current_section.strip():
            sections.append((current_title, current_section.strip()))

        # If no sections found, treat entire text as one section
        if not sections and text.strip():
            sections.append(('Main Content', text.strip()))

        return sections

    def create_chunks_simple(
        self, text: str, post_slug: str, category: str
    ) -> List[ContentChunk]:
        """Create text chunks using simple character-based splitting."""
        if not text or not text.strip():
            return []

        chunks = []
        chunk_size = self.config.chunking.chunk_size
        overlap = self.config.chunking.chunk_overlap
        min_size = self.config.chunking.min_chunk_size

        # Clean the text
        text = self.clean_text(text)

        # Simple chunking by character count with overlap
        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate end position
            end = start + chunk_size

            # If we're not at the end, try to find a good break point
            if end < len(text):
                # Look for sentence ending within the last 100 characters
                search_start = max(start + chunk_size - 100, start)
                sentence_end = text.rfind('.', search_start, end)

                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for paragraph break
                    para_end = text.rfind('\n\n', search_start, end)
                    if para_end > start:
                        end = para_end + 2

            # Extract chunk content
            chunk_content = text[start:end].strip()

            # Skip chunks that are too small
            if len(chunk_content) < min_size:
                start = end
                continue

            # Create chunk
            chunk = ContentChunk(
                chunk_id=f'{category}_{post_slug}_{chunk_index:03d}',
                post_slug=post_slug,
                category=category,
                content=chunk_content,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                word_count=len(chunk_content.split()),
                char_count=len(chunk_content),
            )

            chunks.append(chunk)
            chunk_index += 1

            # Move start position with overlap
            start = max(start + chunk_size - overlap, end - overlap)

            # Prevent infinite loop
            if start >= len(text):
                break

        return chunks

    def create_chunks_langchain(
        self, text: str, post_slug: str, category: str
    ) -> List[ContentChunk]:
        """Create text chunks using LangChain's text splitter."""
        if not LANGCHAIN_AVAILABLE:
            return self.create_chunks_simple(text, post_slug, category)

        if not text or not text.strip():
            return []

        # Configure the text splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunking.chunk_size,
            chunk_overlap=self.config.chunking.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=[
                '\n\n',  # Paragraph breaks
                '\n',  # Line breaks
                '. ',  # Sentence endings
                ', ',  # Clause breaks
                ' ',  # Word breaks
                '',  # Character breaks
            ],
        )

        # Clean the text
        text = self.clean_text(text)

        # Split the text
        text_chunks = splitter.split_text(text)

        # Create ContentChunk objects
        chunks = []
        start_char = 0

        for chunk_index, chunk_content in enumerate(text_chunks):
            if len(chunk_content.strip()) < self.config.chunking.min_chunk_size:
                continue

            # Find the chunk in the original text
            chunk_start = text.find(chunk_content, start_char)
            if chunk_start == -1:
                # Fallback: approximate position
                chunk_start = start_char

            chunk_end = chunk_start + len(chunk_content)

            chunk = ContentChunk(
                chunk_id=f'{category}_{post_slug}_{chunk_index:03d}',
                post_slug=post_slug,
                category=category,
                content=chunk_content.strip(),
                chunk_index=chunk_index,
                start_char=chunk_start,
                end_char=chunk_end,
                word_count=len(chunk_content.split()),
                char_count=len(chunk_content),
            )

            chunks.append(chunk)
            start_char = chunk_end

        return chunks

    def create_chunks_with_sections(
        self, text: str, post_slug: str, category: str
    ) -> List[ContentChunk]:
        """Create chunks preserving section structure when possible."""
        if not text or not text.strip():
            return []

        chunks = []
        sections = self.extract_sections(text)

        chunk_index = 0
        global_start_char = 0

        for section_title, section_content in sections:
            # If section is small enough, keep it as one chunk
            if len(section_content) <= self.config.chunking.chunk_size:
                chunk = ContentChunk(
                    chunk_id=f'{category}_{post_slug}_{chunk_index:03d}',
                    post_slug=post_slug,
                    category=category,
                    content=section_content.strip(),
                    chunk_index=chunk_index,
                    start_char=global_start_char,
                    end_char=global_start_char + len(section_content),
                    word_count=len(section_content.split()),
                    char_count=len(section_content),
                    section_title=section_title,
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # Split large sections into smaller chunks
                section_chunks = self.create_chunks_simple(
                    section_content, post_slug, category
                )

                # Update chunk IDs and add section titles
                for i, chunk in enumerate(section_chunks):
                    chunk.chunk_id = f'{category}_{post_slug}_{chunk_index:03d}'
                    chunk.chunk_index = chunk_index
                    chunk.section_title = section_title
                    chunk.start_char += global_start_char
                    chunk.end_char += global_start_char
                    chunks.append(chunk)
                    chunk_index += 1

            global_start_char += len(section_content) + 2  # +2 for section break

        return chunks

    def create_chunks(
        self, text: str, post_slug: str, category: str
    ) -> List[ContentChunk]:
        """Create text chunks using the configured strategy."""
        if not text or not text.strip():
            return []

        # Choose chunking strategy based on configuration
        if self.config.chunking.preserve_sections:
            return self.create_chunks_with_sections(text, post_slug, category)
        elif LANGCHAIN_AVAILABLE:
            return self.create_chunks_langchain(text, post_slug, category)
        else:
            return self.create_chunks_simple(text, post_slug, category)

    def estimate_reading_time(self, text: str, words_per_minute: int = 200) -> int:
        """Estimate reading time in minutes."""
        if not text:
            return 0

        word_count = len(text.split())
        minutes = max(1, round(word_count / words_per_minute))
        return minutes

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract potential keywords from text."""
        if not text:
            return []

        # Simple keyword extraction based on word frequency
        # Remove common stop words
        stop_words = {
            'the',
            'a',
            'an',
            'and',
            'or',
            'but',
            'in',
            'on',
            'at',
            'to',
            'for',
            'of',
            'with',
            'by',
            'is',
            'are',
            'was',
            'were',
            'be',
            'been',
            'have',
            'has',
            'had',
            'do',
            'does',
            'did',
            'will',
            'would',
            'could',
            'should',
            'may',
            'might',
            'must',
            'can',
            'this',
            'that',
            'these',
            'those',
            'i',
            'you',
            'he',
            'she',
            'it',
            'we',
            'they',
            'me',
            'him',
            'her',
            'us',
            'them',
        }

        # Extract words and count frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}

        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]

        return keywords

    def get_text_stats(self, text: str) -> dict:
        """Get comprehensive statistics about text."""
        if not text:
            return {
                'char_count': 0,
                'word_count': 0,
                'paragraph_count': 0,
                'sentence_count': 0,
                'avg_sentence_length': 0,
                'reading_time_minutes': 0,
            }

        # Basic counts
        char_count = len(text)
        words = text.split()
        word_count = len(words)

        # Paragraph count
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        # Sentence count (approximate)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)

        # Average sentence length
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Reading time
        reading_time = self.estimate_reading_time(text)

        return {
            'char_count': char_count,
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'reading_time_minutes': reading_time,
        }
