# Project: modelstudio-memory-for-hermes

Hermes Agent memory plugin for Alibaba Cloud Bailian (百炼).

## Architecture
- TypeScript plugin for Hermes Agent
- Implements a custom memory provider (NOT Mem0-compatible)
- Communicates with Bailian REST API directly

## Key Constraints
- Bailian API: `https://dashscope.aliyuncs.com/api/v2/apps/memory`
- Auth: DashScope API Key (`sk-xxx` format)
- Rate limits: 120 writes/min, 300 searches/min, 3000 total/min
- Provider must implement Hermes memory interface (add/search/delete/profile)

## Commands
- Build: `npm run build` (tsc)
- After changes: `git add -A && git commit -m "..." && git push`
- Use SSH for git: `git@github.com:Tangruilin/modelstudio-memory-for-hermes.git`

## Style
- TypeScript strict mode
- Async/await for all API calls
- Error handling on every network call
