echo "Running black..."
uv run black src tests
uv run black --check src tests

# 2. isort: Check and apply import sorting
echo "Running isort..."
uv run isort src tests
uv run isort --check src tests

# 3. Ruff: Lint, format, and apply automatic fixes
echo "Running ruff..."
uv run ruff check src tests --fix
uv run ruff format src tests
uv run ruff check src tests