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

"""File validation utilities for uploaded files."""

from __future__ import annotations

import mimetypes
from typing import List, Optional, Tuple

from fastapi import UploadFile


class FileValidator:
    """Validator for uploaded files."""

    # Supported MIME types and their categories
    SUPPORTED_TYPES = {
        # Images
        'image/png': 'image',
        'image/jpeg': 'image',
        'image/jpg': 'image',
        'image/gif': 'image',
        'image/webp': 'image',
        # Text files
        'text/plain': 'text',
        'text/markdown': 'text',
        'text/csv': 'data',
        'application/csv': 'data',
        # Structured data
        'application/json': 'data',
        # Documents
        'application/pdf': 'document',
        # Code files
        'text/html': 'code',
        'text/css': 'code',
        'text/javascript': 'code',
        'application/javascript': 'code',
        'text/python': 'code',
        'application/x-python-code': 'code',
    }

    # File extensions that should be treated as specific MIME types
    EXTENSION_OVERRIDES = {
        '.py': 'text/python',
        '.js': 'text/javascript',
        '.html': 'text/html',
        '.css': 'text/css',
        '.md': 'text/markdown',
        '.json': 'application/json',
        '.csv': 'text/csv',
    }

    # Magic bytes for file type detection
    MAGIC_BYTES = {
        b'\xff\xd8\xff': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF8': 'image/gif',
        b'%PDF': 'application/pdf',
        b'RIFF': 'image/webp',  # Simplified, actual WebP check is more complex
    }

    def __init__(
        self,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        max_files: int = 5,
    ):
        """Initialize file validator.

        Args:
            max_file_size: Maximum file size in bytes.
            max_files: Maximum number of files per upload.
        """
        self.max_file_size = max_file_size
        self.max_files = max_files

    def _detect_mime_type(self, filename: str, content: bytes) -> str:
        """Detect MIME type from filename and content.

        Args:
            filename: Original filename.
            content: First few bytes of file content.

        Returns:
            Detected MIME type.
        """
        # Check extension override first
        for ext, mime_type in self.EXTENSION_OVERRIDES.items():
            if filename.lower().endswith(ext):
                return mime_type

        # Check magic bytes
        for magic, mime_type in self.MAGIC_BYTES.items():
            if content.startswith(magic):
                return mime_type

        # Fall back to mimetypes guess
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    def _validate_content_matches_type(
        self, content: bytes, declared_mime: str
    ) -> bool:
        """Validate that content matches declared MIME type.

        Args:
            content: File content bytes.
            declared_mime: Declared MIME type.

        Returns:
            True if content matches type.
        """
        if not content:
            return False

        # Check magic bytes for common types
        for magic, actual_mime in self.MAGIC_BYTES.items():
            if content.startswith(magic):
                # For WebP, need more specific check
                if magic == b'RIFF' and actual_mime == 'image/webp':
                    return (
                        len(content) >= 12
                        and content[8:12] == b'WEBP'
                        and declared_mime == 'image/webp'
                    )
                return declared_mime == actual_mime

        # For text files, try to decode as UTF-8
        if declared_mime.startswith('text/') or declared_mime == 'application/json':
            try:
                content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                # Try latin-1 as fallback for some text files
                try:
                    content.decode('latin-1')
                    return True
                except UnicodeDecodeError:
                    return False

        # Default to allowing if we can't verify
        return True

    def _check_for_suspicious_content(self, content: bytes) -> List[str]:
        """Basic security check for suspicious content.

        Args:
            content: File content bytes.

        Returns:
            List of warnings/issues found.
        """
        warnings = []

        # Check for executable signatures
        executable_signatures = [
            b'\x4d\x5a',  # Windows PE
            b'\x7fELF',  # Linux ELF
            b'\xca\xfe\xba\xbe',  # Java class
            b'\xfe\xed\xfa',  # Mach-O
        ]

        for sig in executable_signatures:
            if content.startswith(sig):
                warnings.append('File appears to be executable')
                break

        # Check for script injections in text content
        if len(content) > 0:
            try:
                text_content = content.decode('utf-8', errors='ignore').lower()
                suspicious_patterns = [
                    '<script',
                    'javascript:',
                    'vbscript:',
                    'onload=',
                    'onerror=',
                ]

                for pattern in suspicious_patterns:
                    if pattern in text_content:
                        warnings.append(f'Suspicious pattern found: {pattern}')
                        break

            except Exception:
                pass  # Not text content

        return warnings

    async def validate_file(self, file: UploadFile) -> Tuple[bool, List[str]]:
        """Validate a single uploaded file.

        Args:
            file: The uploaded file to validate.

        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []

        # Check filename
        if not file.filename:
            errors.append('File must have a filename')
            return False, errors

        # Check file size (if available)
        if file.size and file.size > self.max_file_size:
            errors.append(
                f'File too large: {file.size} bytes (max: {self.max_file_size} bytes)'
            )

        # Read content for validation
        try:
            content = await file.read()
            await file.seek(0)  # Reset file pointer
        except Exception as e:
            errors.append(f'Error reading file: {e}')
            return False, errors

        # Check actual file size from content
        actual_size = len(content)
        if actual_size > self.max_file_size:
            errors.append(
                f'File too large: {actual_size} bytes (max: {self.max_file_size} bytes)'
            )

        # Detect MIME type
        detected_mime = self._detect_mime_type(file.filename, content)

        # Check if MIME type is supported
        if detected_mime not in self.SUPPORTED_TYPES:
            errors.append(
                f'Unsupported file type: {detected_mime}. '
                f'Supported types: {", ".join(self.SUPPORTED_TYPES.keys())}'
            )

        # Validate content matches declared type
        if not self._validate_content_matches_type(content, detected_mime):
            errors.append('File content does not match detected type')

        # Security checks
        security_warnings = self._check_for_suspicious_content(content)
        if security_warnings:
            errors.extend([f'Security warning: {w}' for w in security_warnings])

        return len(errors) == 0, errors

    async def validate_files(
        self, files: List[UploadFile]
    ) -> Tuple[bool, dict[str, List[str]]]:
        """Validate multiple uploaded files.

        Args:
            files: List of uploaded files to validate.

        Returns:
            Tuple of (all_valid, dict of filename -> errors).
        """
        if len(files) > self.max_files:
            return False, {
                'general': [f'Too many files: {len(files)} (max: {self.max_files})']
            }

        all_valid = True
        validation_results = {}

        for file in files:
            is_valid, errors = await self.validate_file(file)
            if not is_valid:
                all_valid = False
                validation_results[file.filename or 'unknown'] = errors

        return all_valid, validation_results

    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        extensions = set()

        # From extension overrides
        extensions.update(self.EXTENSION_OVERRIDES.keys())

        # From common extensions for supported MIME types
        common_extensions = {
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/gif': ['.gif'],
            'image/webp': ['.webp'],
            'text/plain': ['.txt'],
            'text/markdown': ['.md'],
            'application/pdf': ['.pdf'],
            'text/csv': ['.csv'],
        }

        for mime_type in self.SUPPORTED_TYPES:
            if mime_type in common_extensions:
                extensions.update(common_extensions[mime_type])

        return sorted(list(extensions))
