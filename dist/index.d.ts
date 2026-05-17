export { BailianMemoryClient } from './bailian-client.js';
export { BailianConfig, loadConfig, validateConfig, } from './config.js';
export type { AddMemoryRequest, AddMemoryResponse, SearchMemoryRequest, MemoryNode, SearchMemoryResponse, ListMemoriesResponse, UserProfile, } from './bailian-client.js';
/**
 * Hermes plugin registration placeholder.
 *
 * This will be wired up when integrating with Hermes Agent.
 * Expected interface:
 *
 * export function register(config: BailianConfig): HermesMemoryPlugin {
 *   const client = new BailianMemoryClient(config);
 *   return {
 *     name: 'bailian-memory',
 *     add: (messages) => client.addMemory(config.userId, messages),
 *     search: (query, options) => client.searchMemory(config.userId, query, options?.topK, options?.minScore),
 *     delete: (memoryId) => client.deleteMemory(memoryId),
 *     profile: (schema) => client.getUserProfile(schema),
 *   };
 * }
 */ 
//# sourceMappingURL=index.d.ts.map