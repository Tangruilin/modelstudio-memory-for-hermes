.PHONY: install sync mypy-check pyright-check ruff-check pylint-check format check test

# 安装依赖
install:
	uv sync

# 同步依赖（更新 lock 文件）
sync:
	uv lock

# 格式化代码
format:
	uv run ruff format __init__.py tests/

# mypy 类型检查
mypy-check:
	MYPYPATH=~/.hermes/hermes-agent uv run mypy tests/

# pyright 类型检查
pyright-check:
	npx pyright __init__.py

# ruff lint 检查
ruff-check:
	uv run ruff check __init__.py tests/

# pylint 检查（运行时需要 hermes-agent）
pylint-check:
	PYTHONPATH=~/.hermes/hermes-agent uv run pylint __init__.py tests/ --disable=W0212,R0902,R0903,R0904,C0103

# 运行所有检查
check: ruff-check mypy-check pylint-check

# 运行测试（运行时需要 hermes-agent）
test:
	PYTHONPATH=~/.hermes/hermes-agent uv run pytest tests/ -v