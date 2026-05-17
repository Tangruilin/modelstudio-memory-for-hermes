import { BailianConfig } from './config.js';

export interface AddMemoryRequest {
  user_id: string;
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
  }>;
  source?: string;
}

export interface AddMemoryResponse {
  memory_id: string;
  status: string;
}

export interface SearchMemoryRequest {
  query: string;
  top_k?: number;
  min_score?: number;
}

export interface MemoryNode {
  id: string;
  content: string;
  score?: number;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
}

export interface SearchMemoryResponse {
  memory_nodes: MemoryNode[];
  total: number;
}

export interface ListMemoriesResponse {
  memory_nodes: MemoryNode[];
  total: number;
}

export interface UserProfile {
  user_id: string;
  schema_id: string;
  attributes: Record<string, unknown>;
  updated_at?: string;
}

/**
 * HTTP client for Alibaba Cloud Bailian Memory API.
 *
 * API Documentation:
 * - Base URL: https://dashscope.aliyuncs.com/api/v2/apps/memory
 * - Auth: Bearer token via Authorization header
 * - Rate limits: 120 writes/min, 300 searches/min, 3000 total/min
 */
export class BailianMemoryClient {
  private readonly config: BailianConfig;

  constructor(config: BailianConfig) {
    this.config = config;
  }

  private getHeaders(): Record<string, string> {
    return {
      'Authorization': `Bearer ${this.config.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;

    const response = await fetch(url, {
      method,
      headers: this.getHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Bailian API error: ${response.status} ${response.statusText} - ${errorText}`
      );
    }

    return response.json() as Promise<T>;
  }

  /**
   * Add memory for a user.
   * POST /add
   */
  async addMemory(
    userId: string,
    messages: AddMemoryRequest['messages'],
    source: string = 'hermes'
  ): Promise<AddMemoryResponse> {
    const body: AddMemoryRequest = {
      user_id: userId,
      messages,
      source,
    };

    return this.request<AddMemoryResponse>('POST', '/add', body);
  }

  /**
   * Search memory nodes for a user.
   * POST /memory_nodes/search
   */
  async searchMemory(
    userId: string,
    query: string,
    topK?: number,
    minScore?: number
  ): Promise<SearchMemoryResponse> {
    const body: SearchMemoryRequest = {
      query,
      top_k: topK ?? this.config.topK,
      min_score: minScore ?? this.config.minScore,
    };

    const response = await this.request<{ memory_nodes: MemoryNode[]; total: number }>(
      'POST',
      `/memory_nodes/search?user_id=${encodeURIComponent(userId)}`,
      body
    );

    return response;
  }

  /**
   * List all memory nodes for a user.
   * GET /memory_nodes
   */
  async listMemories(userId: string): Promise<ListMemoriesResponse> {
    return this.request<ListMemoriesResponse>(
      'GET',
      `/memory_nodes?user_id=${encodeURIComponent(userId)}`
    );
  }

  /**
   * Delete a specific memory node.
   * DELETE /memory_nodes/{id}
   */
  async deleteMemory(memoryId: string): Promise<void> {
    await this.request<void>('DELETE', `/memory_nodes/${encodeURIComponent(memoryId)}`);
  }

  /**
   * Get user profile for a specific schema.
   * GET /profile_schemas/{schema}/user_profile
   */
  async getUserProfile(schemaId: string, userId?: string): Promise<UserProfile> {
    const uid = userId ?? this.config.userId;
    return this.request<UserProfile>(
      'GET',
      `/profile_schemas/${encodeURIComponent(schemaId)}/user_profile?user_id=${encodeURIComponent(uid)}`
    );
  }
}