"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadConfig = loadConfig;
exports.validateConfig = validateConfig;
const DEFAULT_BASE_URL = 'https://dashscope.aliyuncs.com/api/v2/apps/memory';
const DEFAULT_TOP_K = 10;
const DEFAULT_MIN_SCORE = 0.5;
/**
 * Load Bailian configuration from environment variables.
 *
 * Environment variables:
 * - DASHSCOPE_API_KEY: API key (required)
 * - BAILIAN_USER_ID: User ID (required)
 * - BAILIAN_BASE_URL: Base URL (optional, defaults to Bailian API)
 * - BAILIAN_AUTO_CAPTURE: Enable auto-capture (optional, default: false)
 * - BAILIAN_AUTO_RECALL: Enable auto-recall (optional, default: false)
 * - BAILIAN_TOP_K: Number of search results (optional, default: 10)
 * - BAILIAN_MIN_SCORE: Minimum relevance score (optional, default: 0.5)
 */
function loadConfig() {
    const apiKey = process.env.DASHSCOPE_API_KEY;
    const userId = process.env.BAILIAN_USER_ID;
    if (!apiKey) {
        throw new Error('DASHSCOPE_API_KEY environment variable is required');
    }
    if (!userId) {
        throw new Error('BAILIAN_USER_ID environment variable is required');
    }
    return {
        apiKey,
        userId,
        baseUrl: process.env.BAILIAN_BASE_URL || DEFAULT_BASE_URL,
        autoCapture: process.env.BAILIAN_AUTO_CAPTURE === 'true',
        autoRecall: process.env.BAILIAN_AUTO_RECALL === 'true',
        topK: parseInt(process.env.BAILIAN_TOP_K || String(DEFAULT_TOP_K), 10),
        minScore: parseFloat(process.env.BAILIAN_MIN_SCORE || String(DEFAULT_MIN_SCORE)),
    };
}
/**
 * Validate a BailianConfig object.
 * Throws an error if the config is invalid.
 */
function validateConfig(config) {
    if (!config.apiKey) {
        throw new Error('apiKey is required');
    }
    if (!config.userId) {
        throw new Error('userId is required');
    }
    if (!config.baseUrl) {
        throw new Error('baseUrl is required');
    }
    if (config.topK < 1) {
        throw new Error('topK must be at least 1');
    }
    if (config.minScore < 0 || config.minScore > 1) {
        throw new Error('minScore must be between 0 and 1');
    }
}
//# sourceMappingURL=config.js.map