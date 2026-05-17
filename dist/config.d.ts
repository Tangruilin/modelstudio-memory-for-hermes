export interface BailianConfig {
    /** DashScope API Key (sk-xxx format) */
    apiKey: string;
    /** User ID for memory operations */
    userId: string;
    /** Base URL for Bailian API */
    baseUrl: string;
    /** Auto-capture messages to memory */
    autoCapture: boolean;
    /** Auto-search memory for context */
    autoRecall: boolean;
    /** Number of results to return from search */
    topK: number;
    /** Minimum relevance score for search results */
    minScore: number;
}
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
export declare function loadConfig(): BailianConfig;
/**
 * Validate a BailianConfig object.
 * Throws an error if the config is invalid.
 */
export declare function validateConfig(config: BailianConfig): void;
//# sourceMappingURL=config.d.ts.map