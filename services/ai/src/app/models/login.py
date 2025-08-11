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

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Request model for login endpoint."""

    secret: str
    name: str = ''


class LoginResponse(BaseModel):
    """Response model for login endpoint."""

    success: bool
    message: str
    session_id: str


class LogoutResponse(BaseModel):
    """Response model for logout endpoint."""

    success: bool
    message: str
