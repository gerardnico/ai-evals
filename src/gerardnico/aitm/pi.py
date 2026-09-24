import json
import sys

from pathlib import Path



def update_base_url(models_path: Path, provider: str, base_url: str, api_key: str | None=None) -> None:
    """
    Set (or update) the base URL for the built-in provider in Pi's
    https://pi.dev/models
    https://pi.dev/docs/latest/configuration#agent-directory
    """

    # Load existing config if present, so we don't clobber other providers.
    if models_path.exists():
        try:
            data = json.loads(models_path.read_text())
        except json.JSONDecodeError as e:
            print(f"Error: {models_path} exists but is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        data = {}

    data.setdefault("providers", {})
    openai_provider = data["providers"].setdefault(provider, {})

    openai_provider["baseUrl"] = base_url
    if api_key is not None:
        openai_provider["apiKey"] = api_key

    models_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Updated {models_path}")
    # print(json.dumps(data, indent=2))
