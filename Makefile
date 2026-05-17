.PHONY: install sync mypy-check pyright-check ruff-check pylint-check format check test

# 安装依赖
install:
	uv sync

# 同步依赖（更新 lock 文件）
sync:
	uv lock

# 格式化代码
format:
	uv run ruff format bailian.py tests/

# mypy 类型检查（使用 stubs）
mypy-check:
	uv run mypy bailian.py tests/

# pyright 类型检查（使用 stubs）
pyright-check:
	npx pyright bailian.py

# ruff lint 检查
ruff-check:
	uv run ruff check bailian.py tests/

# pylint 检查（运行时需要 hermes-agent）
pylint-check:
	PYTHONPATH=~/.hermes/hermes-agent uv run pylint bailian.py tests/ --disable=W0212,R0902,R0903

# 运行所有检查
check: ruff-check mypy-check pylint-check

# 运行测试（运行时需要 hermes-agent）
test:
	PYTHONPATH=~/.hermes/hermes-agent uv run pytest tests/ -v