# modelstudio-memory-for-hermes

Hermes Agent memory plugin for Alibaba Cloud Bailian (百炼) long-term memory service.

## Overview

This plugin integrates Alibaba Cloud Bailian's Memory API as a memory provider for Hermes Agent.

Unlike Mem0-compatible providers, Bailian uses its own REST API protocol.

## API Endpoint

```
https://dashscope.aliyuncs.com/api/v2/apps/memory
```

### Key Operations

| Operation | Path | Method |
|-----------|------|--------|
| Add Memory (sync) | `/add` | POST |
| Add Memory (async) | `/add-async` | POST |
| Search Memory | `/memory_nodes/search` | POST |
| List Memories | `/memory_nodes` | GET |
| Delete Memory | `/memory_nodes/{id}` | DELETE |
| User Profile | `/profile_schemas/{schema}/user_profile` | GET |

### Rate Limits

| API Operation | Rate Limit |
|---------------|------------|
| AddMemory (write) | 120/min |
| SearchMemory (query) | 300/min |
| All operations | 3000/min |

## Configuration

| Config Key | Type | Default | Required |
|------------|------|---------|----------|
| `apiKey` | string | - | Yes |
| `userId` | string | - | Yes |
| `baseUrl` | string | `https://dashscope.aliyuncs.com/api/v2/apps/memory` | No |
| `autoCapture` | boolean | `true` | No |
| `autoRecall` | boolean | `true` | No |
| `topK` | number | `5` | No |
| `minScore` | number | `0` | No |

## Development

Built for Hermes Agent plugin system (TypeScript).

## References

- [阿里云百炼记忆文档](https://help.aliyun.com/zh/model-studio/modelstudio-memory-for-openclaw)
- [OpenClaw 插件源码](https://github.com/modelstudio/modelstudio-memory-for-openclaw)
