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
export declare class BailianMemoryClient {
    private readonly config;
    constructor(config: BailianConfig);
    private getHeaders;
    private request;
    /**
     * Add memory for a user.
     * POST /add
     */
    addMemory(userId: string, messages: AddMemoryRequest['messages'], source?: string): Promise<AddMemoryResponse>;
    /**
     * Search memory nodes for a user.
     * POST /memory_nodes/search
     */
    searchMemory(userId: string, query: string, topK?: number, minScore?: number): Promise<SearchMemoryResponse>;
    /**
     * List all memory nodes for a user.
     * GET /memory_nodes
     */
    listMemories(userId: string): Promise<ListMemoriesResponse>;
    /**
     * Delete a specific memory node.
     * DELETE /memory_nodes/{id}
     */
    deleteMemory(memoryId: string): Promise<void>;
    /**
     * Get user profile for a specific schema.
     * GET /profile_schemas/{schema}/user_profile
     */
    getUserProfile(schemaId: string, userId?: string): Promise<UserProfile>;
}
//# sourceMappingURL=bailian-client.d.ts.map