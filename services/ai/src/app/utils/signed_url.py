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

"""Utility for generating signed URLs for Google Cloud Storage objects."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import google.auth
from google.auth import impersonated_credentials
from google.cloud import storage

_logger = logging.getLogger(__name__)


def generate_download_signed_url(
    uri: str, service_account_email: str, signed_url_lifetime: int
) -> str | None:
    """Generates a signed URL for downloading a GCS object.

    This function creates a short-lived, secure URL that provides temporary
    read access to a file in Google Cloud Storage. It uses impersonated
    credentials to sign the URL, ensuring that the URL is generated on behalf
    of a specific service account.

    Args:
        uri: The GCS URI of the object (e.g., 'gs://bucket-name/path/to/file').
        service_account_email: The email of the service account to use for
            impersonation.
        signed_url_lifetime: The lifetime of the signed URL in minutes.

    Returns:
        The generated signed URL as a string, or None if an error occurred.
    """
    try:
        bucket_name = uri.split('/')[2]
        blob_name = '/'.join(uri.split('/')[3:])
    except IndexError:
        _logger.error('Invalid GCS URI format: %s', uri)
        return None

    try:
        credentials, _ = google.auth.default()

        storage_client = storage.Client()
        data_bucket = storage_client.bucket(bucket_name)
        blob = data_bucket.blob(blob_name)
        expiration = timedelta(minutes=signed_url_lifetime)
        signing_credentials = impersonated_credentials.Credentials(
            source_credentials=credentials,
            target_principal=service_account_email,
            target_scopes=['https://www.googleapis.com/auth/devstorage.read_only'],
            lifetime=signed_url_lifetime,
        )

        signed_url = blob.generate_signed_url(
            expiration=expiration,
            credentials=signing_credentials,
        )
        _logger.info('Successfully generated signed URL for %s', uri)
        return signed_url

    except Exception as e:
        _logger.exception('Error generating signed URL for %s: %s', uri, e)
        return None
