# Bailian Memory Provider for Hermes Agent

阿里云百炼长期记忆服务集成插件。

## 概述

本插件将阿里云百炼的 Memory API 作为 Hermes Agent 的 MemoryProvider 实现，提供跨会话的持久化记忆能力。

不同于 Mem0-compatible providers，百炼使用自定义 REST API 协议。

## 安装

### 1. 获取 DashScope API Key

访问 [DashScope 控制台](https://dashscope.console.aliyun.com/apiKey) 创建 API Key（格式：`sk-xxx`）。

### 2. 配置环境变量

```bash
export DASHSCOPE_API_KEY="sk-your-api-key"
```

### 3. 在 Hermes 中启用

编辑 `~/.hermes/config.yaml`，设置 memory provider：

```yaml
memory:
  provider: bailian
```

或运行交互式配置：

```bash
hermes memory setup
```

## 配置选项

| 配置项 | 类型 | 默认值 | 必需 | 说明 |
|--------|------|--------|------|------|
| `api_key` | string | - | Yes | DashScope API Key |
| `user_id` | string | 自动生成 | No | 用户标识符 |
| `auto_capture` | boolean | true | No | 自动捕获对话到记忆 |
| `auto_recall` | boolean | true | No | 自动预取相关记忆 |
| `top_k` | integer | 5 | No | 搜索结果数量上限 |
| `min_score` | float | 0.0 | No | 搜索相关性阈值 |

## 工具接口

本插件向 Hermes Agent 暴露以下工具：

### bailian_add_memory

存储记忆到百炼长期记忆。

**参数：**

- `content` (string, 必需): 要存储的记忆内容

**示例：**

```json
{
  "content": "用户偏好使用中文进行技术交流"
}
```

### bailian_search_memory

搜索百炼长期记忆。

**参数：**

- `query` (string, 必需): 搜索查询
- `top_k` (integer, 可选): 最大返回数量，默认 5
- `min_score` (float, 可选): 最小相关性阈值，默认 0.0

**示例：**

```json
{
  "query": "用户的编程语言偏好",
  "top_k": 3
}
```

### bailian_list_memories

列出当前用户的所有记忆。

**参数：** 无

### bailian_delete_memory

删除指定记忆。

**参数：**

- `memory_id` (string, 必需): 要删除的记忆 ID

## API 端点

| 操作 | 路径 | 方法 |
|------|------|------|
| 添加记忆（同步） | `/add` | POST |
| 添加记忆（异步） | `/add-async` | POST |
| 搜索记忆 | `/memory_nodes/search` | POST |
| 列出记忆 | `/memory_nodes` | GET |
| 删除记忆 | `/memory_nodes/{id}` | DELETE |
| 用户画像 | `/profile_schemas/{schema}/user_profile` | GET |

基础 URL: `https://dashscope.aliyuncs.com/api/v2/apps/memory`

## 速率限制

| API 操作 | 速率限制 |
|----------|----------|
| AddMemory (写入) | 120/min |
| SearchMemory (查询) | 300/min |
| 所有操作 | 3000/min |

## 开发

### 测试导入

```bash
python -c "from bailian import BailianMemoryProvider; print('OK')"
```

### 运行单元测试

```bash
make test
```

### 运行代码检查

```bash
make check
```

## 参考

- [阿里云百炼记忆文档](https://help.aliyun.com/zh/model-studio/modelstudio-memory-for-openclaw)
- [OpenClaw 插件源码](https://github.com/modelstudio/modelstudio-memory-for-openclaw)
- [Hermes MemoryProvider ABC](https://github.com/hermes-agent/hermes-agent/blob/main/agent/memory_provider.py)