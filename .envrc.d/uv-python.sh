export VIRTUAL_ENV="$PROJECT_ROOT/.venv"
export UV_PROJECT_ENVIRONMENT="$VIRTUAL_ENV"

# creates .venv + installs deps automatically
uv sync

# activate
if [ -f ".venv/Scripts/activate" ]; then
  # Windows (Git Bash / WSL boundary)
  source .venv/Scripts/activate
else
  # Linux/macOS
  source .venv/bin/activate
fi
