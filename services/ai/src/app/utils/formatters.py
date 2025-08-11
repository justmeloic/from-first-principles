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

"""Utility functions for formatting agent responses."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from fastapi import Request

from src.app.core.config import settings
from src.app.utils.signed_url import generate_download_signed_url

_logger = logging.getLogger(__name__)

_REFERENCE_TOKEN = '<START_OF_REFERENCE_DOCUMENTS>'
_CITATION_PATTERN = re.compile(r'(\[[0-9,\s]+\])')


def _parse_references(references_text: str, session_id: str | None) -> dict[str, Any]:
    """Parses a JSON string of references into a formatted dictionary.

    Args:
        references_text: A string containing a JSON list of reference dicts.
        session_id: The session ID for logging purposes.

    Returns:
        A dictionary of formatted reference documents or an empty dict on error.
    """
    try:
        references_list = json.loads(references_text)
        if not isinstance(references_list, list):
            _logger.warning(
                'References text is not a JSON list for session %s.', session_id
            )
            return {}

        return {
            str(i + 1): {
                'title': ref.get('title', ''),
                'link': ref.get('link', ''),
                'text': ref.get('text', ''),
            }
            for i, ref in enumerate(references_list)
            if isinstance(ref, dict)
        }
    except json.JSONDecodeError as e:
        _logger.error(
            'Failed to parse references JSON for session %s: %s\nContent: %s',
            session_id,
            e,
            references_text[:200],
        )
        return {}


def _format_citations(text: str) -> str:
    """Finds and bolds inline citations in a block of text.

    Args:
        text: The text to format.

    Returns:
        The text with Markdown bolding applied to any citations like `[1]`.
    """
    return _CITATION_PATTERN.sub(r'**\1**', text)


def _parse_processed_agreements(
    agreements_text: str, session_id: str | None
) -> dict[str, Any]:
    """Parses a JSON string of processed agreement filenames into a dict.

    Args:
        agreements_text: A string containing a JSON list of agreement filenames.
        session_id: The session ID for logging purposes.

    Returns:
        A dictionary of formatted processed agreements or an empty dict on error.
    """
    try:
        agreements_list = json.loads(agreements_text)
        if not isinstance(agreements_list, list):
            _logger.warning(
                'Processed agreements text is not a JSON list for session %s.',
                session_id,
            )
            return {}

        processed_agreements_references = {}
        gcs_bucket = settings.GCS_BUCKET_NAME

        for i, filename in enumerate(agreements_list):
            if not isinstance(filename, str):
                continue

            key = str(i + 1)
            title = filename
            text = f'Processed agreement: {filename}'
            link = ''

            if settings.FILE_ACCESS_METHOD.lower() == 'gcs':
                uri = (
                    f'gs://{gcs_bucket}/locals/{filename}'
                    if filename.endswith('Locals.pdf')
                    else f'gs://{gcs_bucket}/agreements/{filename}'
                )
                signed_url = generate_download_signed_url(
                    uri,
                    settings.SERVICE_ACCOUNT_EMAIL,
                    settings.SIGNED_URL_LIFETIME,
                )
                url_auth = uri.replace('gs://', 'https://storage.cloud.google.com/')

                link = signed_url or url_auth
            else:  # Local file access
                relative_path = (
                    f'locals/{filename}'
                    if filename.endswith('Locals.pdf')
                    else f'agreements/{filename}'
                )
                link = f'/api/v1/files/{relative_path}'

            processed_agreements_references[key] = {
                'title': title,
                'link': link,
                'text': text,
            }

        return processed_agreements_references
    except json.JSONDecodeError as e:
        _logger.error(
            'Failed to parse processed agreements JSON for session %s: %s\nContent: %s',
            session_id,
            e,
            agreements_text[:200],
        )
        return {}


def format_text_response(
    response_text: str, request: Request
) -> tuple[str, dict[str, Any]]:
    """Formats the raw text response from an agent.

    This function separates the main response text from reference documents,
    formats the references into a structured dictionary, and adds Markdown
    bolding to any inline citations (e.g., `[1]`) in the main text.

    Args:
        response_text: The raw string response from the agent.
        request: The FastAPI request, used to access the session ID for logging.

    Returns:
        A tuple containing:
            - The formatted response text with bolded citations.
            - A dictionary of parsed reference documents.
    """
    main_text, _, references_text = response_text.partition(_REFERENCE_TOKEN)

    formatted_text = _format_citations(main_text.strip())

    if references_text:
        session_id = getattr(request.state, 'actual_session_id', None)

        # Try to detect the type of references by attempting to parse as JSON
        try:
            parsed_data = json.loads(references_text.strip())

            # Check if it's a list of strings (processed agreements)
            if isinstance(parsed_data, list) and all(
                isinstance(item, str) for item in parsed_data
            ):
                references_json = _parse_processed_agreements(
                    references_text.strip(), session_id
                )
            # Check if it's a list of dicts (traditional document references)
            elif isinstance(parsed_data, list) and all(
                isinstance(item, dict) for item in parsed_data
            ):
                references_json = _parse_references(references_text.strip(), session_id)
            else:
                _logger.warning(
                    'Unknown reference format for session %s. Using default parser.',
                    session_id,
                )
                references_json = _parse_references(references_text.strip(), session_id)
        except json.JSONDecodeError:
            # Fallback to traditional reference parsing
            references_json = _parse_references(references_text.strip(), session_id)
    else:
        references_json = {}

    return (formatted_text, references_json)
