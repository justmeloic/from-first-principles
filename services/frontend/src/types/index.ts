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

export interface ChatMessage {
  role: "user" | "bot";
  content: string;
}

export interface Reference {
  title: string;
  link?: string;
  description?: string;
  source?: string;
  page?: number;
  section?: string;
  url?: string;
}

export interface MessageResponse {
  response: string;
  references?: { [key: string]: Reference };
  session_id?: string;
  model?: string;
  confidence?: number;
}

export interface Model {
  name: string;
  description?: string;
  provider?: string;
  max_tokens?: number;
}

export interface ModelsResponse {
  models: Record<string, Model>;
  default_model: string;
}

export interface QueryRequest {
  text: string;
  model?: string;
}
