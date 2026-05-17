.PHONY: install sync mypy-check pyright-check ruff-check format check test

HERMES_SRC := /Users/reilly/.hermes/hermes-agent
export PYTHONPATH := $(HERMES_SRC):$(PYTHONPATH)

# 安装依赖
install:
	uv sync

# 同步依赖（更新 lock 文件）
sync:
	uv lock

# 格式化代码
format:
	uv run ruff format plugins/ tests/

# mypy 类型检查
mypy-check:
	uv run mypy plugins/ tests/

# pyright 类型检查
pyright-check:
	npx pyright /Users/reilly/GithubProject/Python/modelstudio-memory-for-hermes/plugins/

# ruff lint 检查
ruff-check:
	uv run ruff check plugins/ tests/

# pylint 检查（禁用测试中合理的警告）
pylint-check:
	uv run pylint plugins/ tests/ --disable=W0212,R0902,R0903

# 运行所有检查
check: ruff-check mypy-check pylint-check

# 运行测试
test:
	uv run pytest tests/ -v