"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateConfig = exports.loadConfig = exports.BailianMemoryClient = void 0;
var bailian_client_js_1 = require("./bailian-client.js");
Object.defineProperty(exports, "BailianMemoryClient", { enumerable: true, get: function () { return bailian_client_js_1.BailianMemoryClient; } });
var config_js_1 = require("./config.js");
Object.defineProperty(exports, "loadConfig", { enumerable: true, get: function () { return config_js_1.loadConfig; } });
Object.defineProperty(exports, "validateConfig", { enumerable: true, get: function () { return config_js_1.validateConfig; } });
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
//# sourceMappingURL=index.js.map