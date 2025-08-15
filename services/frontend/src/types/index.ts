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

export interface SearchQuery {
  query: string;
  search_type: 'semantic' | 'keyword' | 'hybrid';
  limit?: number;
  category_filter?: 'blog' | 'engineering';
  similarity_threshold?: number;
  case_sensitive?: boolean;
}

export interface SearchResult {
  title: string;
  category: string;
  slug: string;
  excerpt: string;
  content: string;
  score: number;
  url: string;
  publish_date: string;
  tags: string[];
  metadata: Record<string, any>;
}

export interface SearchResponse {
  query: Record<string, any>;
  results: SearchResult[];
  total_results: number;
  search_time_ms: number;
  metadata: Record<string, any>;
}

export interface SearchStats {
  database_available: boolean;
  categories: Record<string, {
    posts: number;
    chunks: number;
    last_updated: string;
  }>;
  database: {
    location: string;
    table_name: string;
    size: string;
  };
  embedding_info: {
    name: string;
    device: string;
    max_seq_length: number;
    embedding_dimension: number;
  };
  total_chunks: number;
}

export interface SearchHealth {
  status: string;
  pipeline_available: boolean;
  database_available: boolean;
  test_search_successful: boolean;
  sample_results_count: number;
}
