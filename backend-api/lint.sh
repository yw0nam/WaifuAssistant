uv run black src tests
uv run black --check src tests

uv run isort src tests
uv run isort --check src tests

uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests