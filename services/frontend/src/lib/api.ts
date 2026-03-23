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

import { MessageResponse, ModelsResponse, SearchHealth, SearchQuery, SearchResponse, SearchStats, SSEEvent } from "@/types";

// Use environment variable with fallback;
// setting the fallback to an empty string will cause the frontend
// to use relative paths for API requests.
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

// Common headers to include in all API requests.
// 'ngrok-skip-browser-warning' bypasses the ngrok free-tier interstitial page.
const COMMON_HEADERS: Record<string, string> = {
  'ngrok-skip-browser-warning': 'true',
};

export interface SendMessageOptions {
  model?: string;
  signal?: AbortSignal;
}

export const sendMessage = async (
  message: string,
  files?: File[],
  options?: SendMessageOptions
): Promise<MessageResponse> => {
  try {
    const storedSessionId = localStorage.getItem('agentChatSessionId');

    // Always use FormData since the backend expects Form/File parameters
    const formData = new FormData();
    formData.append('text', message);

    if (options?.model) {
      formData.append('model', options.model);
    }

    // Add files if provided
    if (files && files.length > 0) {
      files.forEach((file) => {
        formData.append('files', file);
      });
    }

    const response = await fetch(`${BASE_URL}/api/v1/root_agent/`, {
      method: 'POST',
      headers: {
        ...COMMON_HEADERS,
        'X-Session-ID': storedSessionId || '', // Don't set Content-Type for FormData
      },
      body: formData,
      signal: options?.signal,
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

/**
 * Stream a message to the agent and yield SSE events as they arrive.
 * Enables real-time token-by-token response display.
 */
export async function* streamMessage(
  message: string,
  files?: File[],
  options?: SendMessageOptions
): AsyncGenerator<SSEEvent, void, unknown> {
  const storedSessionId = localStorage.getItem('agentChatSessionId');

  const formData = new FormData();
  formData.append('text', message);

  if (options?.model) {
    formData.append('model', options.model);
  }

  if (files && files.length > 0) {
    files.forEach((file) => {
      formData.append('files', file);
    });
  }

  const response = await fetch(`${BASE_URL}/api/v1/root_agent/stream`, {
    method: 'POST',
    headers: {
      ...COMMON_HEADERS,
      'X-Session-ID': storedSessionId || '',
    },
    body: formData,
    signal: options?.signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Update session ID from response
  const newSessionId = response.headers.get('x-session-id');
  if (newSessionId) {
    if (storedSessionId && storedSessionId !== newSessionId) {
      localStorage.removeItem('agentChatHistory');
      localStorage.removeItem('agentChatReferences');
      localStorage.removeItem('agentIsFirstPrompt');
    }
    localStorage.setItem('agentChatSessionId', newSessionId);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages (separated by double newlines)
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // Keep incomplete message in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data as SSEEvent;
          } catch (e) {
            console.warn('Failed to parse SSE event:', line);
          }
        }
      }
    }

    // Process any remaining data in buffer
    if (buffer.startsWith('data: ')) {
      try {
        const data = JSON.parse(buffer.slice(6));
        yield data as SSEEvent;
      } catch (e) {
        // Ignore incomplete final chunk
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export const getAvailableModels = async (): Promise<ModelsResponse> => {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/root_agent/models`, {
      method: 'GET',
      headers: {
        ...COMMON_HEADERS,
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
      ...COMMON_HEADERS,
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
      ...COMMON_HEADERS,
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

export const searchContent = async (
  searchQuery: SearchQuery,
  options?: { signal?: AbortSignal }
): Promise<SearchResponse> => {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/search/`, {
      method: 'POST',
      headers: {
        ...COMMON_HEADERS,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchQuery),
      signal: options?.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to search content:', error);
    throw error;
  }
};

export const getSearchStats = async (): Promise<SearchStats> => {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/search/stats`, {
      method: 'GET',
      headers: {
        ...COMMON_HEADERS,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch search stats:', error);
    throw error;
  }
};

export const getSearchHealth = async (): Promise<SearchHealth> => {
  try {
    const response = await fetch(`${BASE_URL}/api/v1/search/health`, {
      method: 'GET',
      headers: {
        ...COMMON_HEADERS,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to check search health:', error);
    throw error;
  }
};
