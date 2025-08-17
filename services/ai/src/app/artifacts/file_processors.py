# Copyright 2025 Loïc Muhirwa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""File processors for different MIME types with minimal dependencies.

This module provides processors for various file types that extract content
and metadata from uploaded files for use by AI agents.
"""

from __future__ import annotations

import csv
import io
import json
from abc import ABC, abstractmethod
from typing import Dict

from loguru import logger as _logger


class FileProcessor(ABC):
    """Base class for file processors."""

    @abstractmethod
    async def process(self, data: bytes) -> str:
        """Process file data and return extracted content."""
        pass


class TextProcessor(FileProcessor):
    """Process plain text files."""

    async def process(self, data: bytes) -> str:
        """Extract text content from text files."""
        try:
            # Try UTF-8 first, fall back to latin-1
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                content = data.decode('latin-1')

            # Basic cleanup and info
            lines = content.splitlines()
            word_count = len(content.split())
            char_count = len(content)

            return (
                f'Text file content ({len(lines)} lines, '
                f'{word_count} words, {char_count} characters):\n\n{content}'
            )
        except Exception as e:
            _logger.error(f'Error processing text file: {e}')
            return f'Error processing text file: {e}'


class JSONProcessor(FileProcessor):
    """Process JSON files."""

    async def process(self, data: bytes) -> str:
        """Extract and format JSON content."""
        try:
            content = data.decode('utf-8')
            parsed_json = json.loads(content)

            # Provide structure info
            def analyze_structure(obj, depth=0):
                if depth > 3:  # Limit recursion
                    return '...'

                if isinstance(obj, dict):
                    if not obj:
                        return '{}'
                    items = []
                    for key, value in list(obj.items())[:5]:  # Show first 5 keys
                        items.append(f'"{key}": {analyze_structure(value, depth + 1)}')
                    if len(obj) > 5:
                        items.append('...')
                    return '{' + ', '.join(items) + '}'
                elif isinstance(obj, list):
                    if not obj:
                        return '[]'
                    return (
                        f'[{len(obj)} items: {analyze_structure(obj[0], depth + 1)}...]'
                    )
                elif isinstance(obj, str):
                    return f'"{obj[:50]}{"..." if len(obj) > 50 else ""}"'
                else:
                    return str(obj)

            structure = analyze_structure(parsed_json)

            return (
                f'JSON file structure:\n{structure}\n\n'
                f'Full content:\n{json.dumps(parsed_json, indent=2)}'
            )
        except json.JSONDecodeError as e:
            return f'Invalid JSON file: {e}'
        except Exception as e:
            _logger.error(f'Error processing JSON file: {e}')
            return f'Error processing JSON file: {e}'


class CSVProcessor(FileProcessor):
    """Process CSV files."""

    async def process(self, data: bytes) -> str:
        """Extract and analyze CSV content."""
        try:
            content = data.decode('utf-8')

            # Try different delimiters
            delimiters = [',', ';', '\t', '|']
            best_delimiter = ','
            max_columns = 0

            for delimiter in delimiters:
                try:
                    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
                    first_row = next(reader, [])
                    if len(first_row) > max_columns:
                        max_columns = len(first_row)
                        best_delimiter = delimiter
                except Exception:
                    continue

            # Parse with best delimiter
            reader = csv.reader(io.StringIO(content), delimiter=best_delimiter)
            rows = list(reader)

            if not rows:
                return 'Empty CSV file'

            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []

            # Create summary
            summary = [
                f'CSV file analysis:',
                f'- Columns: {len(headers)} ({", ".join(headers[:10])}{"..." if len(headers) > 10 else ""})',
                f'- Rows: {len(data_rows)} data rows',
                f"- Delimiter: '{best_delimiter}'",
                '',
                'Sample data (first 5 rows):',
            ]

            # Show sample data
            for i, row in enumerate(rows[:6]):  # Header + 5 data rows
                if i == 0:
                    summary.append(f'Headers: {row}')
                else:
                    summary.append(f'Row {i}: {row}')

            return '\n'.join(summary)

        except Exception as e:
            _logger.error(f'Error processing CSV file: {e}')
            return f'Error processing CSV file: {e}'


class ImageProcessor(FileProcessor):
    """Process image files using basic analysis."""

    async def process(self, data: bytes) -> str:
        """Extract basic image information."""
        try:
            # Try to import PIL for better image analysis
            try:
                from PIL import Image

                image = Image.open(io.BytesIO(data))

                return (
                    f'Image file information:\n'
                    f'- Format: {image.format}\n'
                    f'- Size: {image.size[0]}x{image.size[1]} pixels\n'
                    f'- Mode: {image.mode}\n'
                    f'- File size: {len(data)} bytes'
                )
            except ImportError:
                # Fall back to basic analysis
                file_size = len(data)

                # Basic format detection based on magic bytes
                format_info = 'Unknown'
                if data.startswith(b'\xff\xd8\xff'):
                    format_info = 'JPEG'
                elif data.startswith(b'\x89PNG\r\n\x1a\n'):
                    format_info = 'PNG'
                elif data.startswith(b'GIF8'):
                    format_info = 'GIF'
                elif data.startswith(b'RIFF') and b'WEBP' in data[:20]:
                    format_info = 'WebP'

                return (
                    f'Image file information (basic analysis):\n'
                    f'- Detected format: {format_info}\n'
                    f'- File size: {file_size} bytes\n'
                    f'Note: Install Pillow for detailed image analysis'
                )

        except Exception as e:
            _logger.error(f'Error processing image file: {e}')
            return f'Error processing image file: {e}'


class PDFProcessor(FileProcessor):
    """Process PDF files."""

    async def process(self, data: bytes) -> str:
        """Extract text content from PDF files."""
        try:
            # Try to import PyPDF2 for PDF processing
            try:
                import PyPDF2

                pdf_file = io.BytesIO(data)
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                num_pages = len(pdf_reader.pages)
                text_content = []

                # Extract text from first few pages
                max_pages_to_extract = min(5, num_pages)
                for page_num in range(max_pages_to_extract):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f'--- Page {page_num + 1} ---\n{text}')

                extracted_text = '\n\n'.join(text_content)

                return (
                    f'PDF file analysis:\n'
                    f'- Total pages: {num_pages}\n'
                    f'- File size: {len(data)} bytes\n'
                    f'- Extracted text from first {max_pages_to_extract} pages:\n\n'
                    f'{extracted_text}'
                )

            except ImportError:
                return (
                    f'PDF file detected:\n'
                    f'- File size: {len(data)} bytes\n'
                    f'- Cannot extract text content (PyPDF2 not installed)\n'
                    f'- Install PyPDF2 to enable PDF text extraction'
                )

        except Exception as e:
            _logger.error(f'Error processing PDF file: {e}')
            return f'Error processing PDF file: {e}'


class CodeProcessor(FileProcessor):
    """Process code files."""

    async def process(self, data: bytes) -> str:
        """Analyze code files."""
        try:
            content = data.decode('utf-8')
            lines = content.splitlines()

            # Basic code analysis
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])
            comment_lines = len(
                [
                    line
                    for line in lines
                    if line.strip().startswith(('#', '//', '/*', '*', '--'))
                ]
            )

            # Try to detect language patterns
            language_hints = []
            if 'def ' in content or 'import ' in content:
                language_hints.append('Python')
            if 'function ' in content or 'const ' in content or 'let ' in content:
                language_hints.append('JavaScript')
            if '#include' in content or 'int main' in content:
                language_hints.append('C/C++')
            if 'class ' in content and '{' in content:
                language_hints.append('Java/C#')

            return (
                f'Code file analysis:\n'
                f'- Total lines: {total_lines}\n'
                f'- Non-empty lines: {non_empty_lines}\n'
                f'- Comment lines: {comment_lines}\n'
                f'- Possible languages: {", ".join(language_hints) if language_hints else "Unknown"}\n\n'
                f'Content:\n{content}'
            )

        except Exception as e:
            _logger.error(f'Error processing code file: {e}')
            return f'Error processing code file: {e}'


class FileProcessorFactory:
    """Factory for creating appropriate file processors based on MIME type."""

    _processors: Dict[str, FileProcessor] = {
        # Text files
        'text/plain': TextProcessor(),
        'text/markdown': TextProcessor(),
        'text/html': CodeProcessor(),
        'text/css': CodeProcessor(),
        'text/javascript': CodeProcessor(),
        'application/javascript': CodeProcessor(),
        'text/python': CodeProcessor(),
        'application/json': JSONProcessor(),
        'text/csv': CSVProcessor(),
        'application/csv': CSVProcessor(),
        # Images
        'image/png': ImageProcessor(),
        'image/jpeg': ImageProcessor(),
        'image/jpg': ImageProcessor(),
        'image/gif': ImageProcessor(),
        'image/webp': ImageProcessor(),
        # Documents
        'application/pdf': PDFProcessor(),
    }

    @classmethod
    def get_processor(cls, mime_type: str) -> FileProcessor:
        """Get appropriate processor for MIME type."""
        processor = cls._processors.get(mime_type.lower())
        if processor:
            return processor

        # Fall back to basic processors based on primary type
        primary_type = mime_type.split('/')[0].lower()
        if primary_type == 'text':
            return TextProcessor()
        elif primary_type == 'image':
            return ImageProcessor()
        else:
            # Default to text processor for unknown types
            return TextProcessor()


def get_file_processor(mime_type: str) -> FileProcessor:
    """Convenience function to get a file processor."""
    return FileProcessorFactory.get_processor(mime_type)
