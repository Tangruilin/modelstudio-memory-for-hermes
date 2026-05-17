"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BailianMemoryClient = void 0;
/**
 * HTTP client for Alibaba Cloud Bailian Memory API.
 *
 * API Documentation:
 * - Base URL: https://dashscope.aliyuncs.com/api/v2/apps/memory
 * - Auth: Bearer token via Authorization header
 * - Rate limits: 120 writes/min, 300 searches/min, 3000 total/min
 */
class BailianMemoryClient {
    config;
    constructor(config) {
        this.config = config;
    }
    getHeaders() {
        return {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json',
        };
    }
    async request(method, path, body) {
        const url = `${this.config.baseUrl}${path}`;
        const response = await fetch(url, {
            method,
            headers: this.getHeaders(),
            body: body ? JSON.stringify(body) : undefined,
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Bailian API error: ${response.status} ${response.statusText} - ${errorText}`);
        }
        return response.json();
    }
    /**
     * Add memory for a user.
     * POST /add
     */
    async addMemory(userId, messages, source = 'hermes') {
        const body = {
            user_id: userId,
            messages,
            source,
        };
        return this.request('POST', '/add', body);
    }
    /**
     * Search memory nodes for a user.
     * POST /memory_nodes/search
     */
    async searchMemory(userId, query, topK, minScore) {
        const body = {
            query,
            top_k: topK ?? this.config.topK,
            min_score: minScore ?? this.config.minScore,
        };
        const response = await this.request('POST', `/memory_nodes/search?user_id=${encodeURIComponent(userId)}`, body);
        return response;
    }
    /**
     * List all memory nodes for a user.
     * GET /memory_nodes
     */
    async listMemories(userId) {
        return this.request('GET', `/memory_nodes?user_id=${encodeURIComponent(userId)}`);
    }
    /**
     * Delete a specific memory node.
     * DELETE /memory_nodes/{id}
     */
    async deleteMemory(memoryId) {
        await this.request('DELETE', `/memory_nodes/${encodeURIComponent(memoryId)}`);
    }
    /**
     * Get user profile for a specific schema.
     * GET /profile_schemas/{schema}/user_profile
     */
    async getUserProfile(schemaId, userId) {
        const uid = userId ?? this.config.userId;
        return this.request('GET', `/profile_schemas/${encodeURIComponent(schemaId)}/user_profile?user_id=${encodeURIComponent(uid)}`);
    }
}
exports.BailianMemoryClient = BailianMemoryClient;
//# sourceMappingURL=bailian-client.js.map