import json
import sys
from importlib import resources
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

DEFAULT_CACHE_PATH = Path.home().joinpath(".tokenlists")

UNISWAP_ENS_TOKENLISTS_HOST = "https://wispy-bird-88a7.uniswap.workers.dev/?url=http://{}.link"
SUGGESTED_TOKENLISTS_SOURCE_URL = (
    "https://raw.githubusercontent.com/Uniswap/tokenlists-org/master/src/token-lists.json"
)


def get_local_tokenlists_config() -> dict[str, Any] | None:
    pyproject_path = _find_local_pyproject_path()
    if pyproject_path is None:
        return None

    data = tomllib.loads(pyproject_path.read_text())
    tool_config = data.get("tool", {})
    if not isinstance(tool_config, dict):
        return None

    tokenlists_config = tool_config.get("tokenlists")
    return tokenlists_config if isinstance(tokenlists_config, dict) else None


def get_tokenlist_order() -> list[str] | None:
    tokenlists_config = get_local_tokenlists_config()
    if tokenlists_config is None:
        return None

    order = tokenlists_config.get("order", [])
    if not isinstance(order, list) or not all(isinstance(item, str) for item in order):
        raise ValueError(
            "Expected `[tool.tokenlists].order` in `pyproject.toml` to be a list of strings."
        )

    return order


def get_suggested_tokenlists() -> dict[str, dict[str, str]]:
    suggested_tokenlists = resources.files("tokenlists").joinpath("suggested.json")
    return json.loads(suggested_tokenlists.read_text())


def _find_local_pyproject_path() -> Path | None:
    current_path = Path.cwd().resolve()
    for directory in (current_path, *current_path.parents):
        pyproject_path = directory.joinpath("pyproject.toml")
        if pyproject_path.is_file():
            return pyproject_path

    return None
