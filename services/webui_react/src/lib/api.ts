/**
 * Copyright 2025 Loïc Muhirwa
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { MessageResponse, ModelsResponse } from "@/types";

// Use environment variable with fallback;
// setting the fallback to an empty string will cause the frontend
// to use relative paths for API requests.
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export interface SendMessageOptions {
  model?: string;
  signal?: AbortSignal;
}

export const sendMessage = async (
  message: string,
  options?: SendMessageOptions
): Promise<MessageResponse> => {
  try {
    const storedSessionId = localStorage.getItem('agentChatSessionId');

    const requestBody: { text: string; model?: string } = { text: message };
    if (options?.model) {
      requestBody.model = options.model;
    }

    const response = await fetch(`${BASE_URL}/api/v1/root_agent/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': storedSessionId || '', // Always send the header, even if empty
      },
      body: JSON.stringify(requestBody),
      signal: options?.signal, // Add abort signal support
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get session ID from response header and store it if present
    const newSessionId = response.headers.get('x-session-id'); // Note: header names are case-insensitive
    if (newSessionId) {
      // If session ID changed, clear the chat data (indicates new session)
      if (storedSessionId && storedSessionId !== newSessionId) {
        localStorage.removeItem('agentChatHistory');
        localStorage.removeItem('agentChatReferences');
        localStorage.removeItem('agentIsFirstPrompt');
        console.log('Session ID changed, cleared chat data');
      }

      localStorage.setItem('agentChatSessionId', newSessionId);
      console.log('Stored new session ID:', newSessionId); // Debug logging
    } else {
      console.warn('No session ID received from server'); // Debug logging
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
};

export const getAvailableModels = async (): Promise<ModelsResponse> => {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/root_agent/models`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch available models:', error);
    throw error;
  }
};

export const hasExistingSession = (): boolean => {
  return !!localStorage.getItem('agentChatSessionId');
};

export const startNewSession = (): void => {
  // Clear the stored session ID to force creation of a new session
  localStorage.removeItem('agentChatSessionId');
  // Clear persisted chat data
  localStorage.removeItem('agentChatHistory');
  localStorage.removeItem('agentChatReferences');
  localStorage.removeItem('agentIsFirstPrompt');
  console.log('Cleared session ID and chat data - next request will create a new session');
};

export const login = async (secret: string, name: string) => {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ secret, name }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Login failed');
  }

  const newSessionId = response.headers.get('x-session-id');
  if (newSessionId) {
    localStorage.setItem('agentChatSessionId', newSessionId);
  }

  return response.json();
};

export const logout = async () => {
  const storedSessionId = localStorage.getItem('agentChatSessionId');
  const response = await fetch(`${BASE_URL}/api/v1/auth/logout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': storedSessionId || '',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Logout failed');
  }

  // Clear all session and chat data
  localStorage.removeItem('agentChatSessionId');
  localStorage.removeItem('agentChatHistory');
  localStorage.removeItem('agentChatReferences');
  localStorage.removeItem('agentIsFirstPrompt');
  return response.json();
};
