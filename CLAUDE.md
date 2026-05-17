# Project: modelstudio-memory-for-hermes

Hermes Agent memory plugin for Alibaba Cloud Bailian (百炼).

## Architecture
- **Python** plugin for Hermes Agent (NOT TypeScript/JS)
- Plugin type: Memory Provider
- Extends `MemoryProvider` from `agent/memory_provider.py`
- Communicates with Bailian REST API directly
- Target install path: `plugins/memory/bailian/`

## Plugin Structure
```
plugins/memory/bailian/
├── __init__.py      # BailianMemoryProvider class + register() entry point
├── plugin.yaml       # Metadata (name, description, hooks)
└── README.md         # Setup instructions
```

## Key Constraints
- Bailian API: `https://dashscope.aliyuncs.com/api/v2/apps/memory`
- Auth: DashScope API Key (`sk-xxx` format)
- Rate limits: 120 writes/min, 300 searches/min, 3000 total/min
- NOT Mem0-compatible — implements custom REST client

## Required Methods (MemoryProvider ABC)
- `name` → `"bailian"`
- `is_available()` → check DASHSCOPE_API_KEY in env
- `initialize(session_id, **kwargs)` → set up API client
- `get_tool_schemas()` → return OpenAI-format tool schemas
- `handle_tool_call(name, args)` → dispatch tool calls
- `get_config_schema()` → config fields for `hermes memory setup`
- Optional: `prefetch()`, `sync_turn()`, `system_prompt_block()`, etc.

## Reference
- Hermes MemoryProvider ABC: `agent/memory_provider.py` in hermes-agent source
- Bailian API docs: https://help.aliyun.com/zh/model-studio/modelstudio-memory-for-openclaw
- OpenClaw plugin source (for reference): https://github.com/modelstudio/modelstudio-memory-for-openclaw

## Commands
- Test: `python -c "from plugins.memory.bailian import BailianMemoryProvider; print('OK')"`
- After changes: `git add -A && git commit -m "..." && git push`

## Style
- Python 3.11+
- Type hints on all functions
- Docstrings in Google style
- Use `requests` library for HTTP calls
- Error handling on every network call
