import json

import pytest

from tokenlists import TokenListManager
from tokenlists import config


def test_get_token_info_uses_local_pyproject_order(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    tmp_path.joinpath("pyproject.toml").write_text(
        """
[tool.tokenlists]
order = ["Beta", "Alpha"]
""".strip()
    )

    _write_tokenlist(cache_path, "Alpha", _token("TKN", "0x0000000000000000000000000000000000000001"))
    _write_tokenlist(cache_path, "Beta", _token("TKN", "0x0000000000000000000000000000000000000002"))

    token_info = TokenListManager().get_token_info("TKN")
    assert token_info.address == "0x0000000000000000000000000000000000000002"


def test_get_tokens_without_name_iterates_across_configured_order(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    tmp_path.joinpath("pyproject.toml").write_text(
        """
[tool.tokenlists]
order = ["Beta"]
""".strip()
    )

    _write_tokenlist(cache_path, "Alpha", _token("AAA", "0x0000000000000000000000000000000000000001"))
    _write_tokenlist(cache_path, "Beta", _token("BBB", "0x0000000000000000000000000000000000000002"))

    symbols = [token.symbol for token in TokenListManager().get_tokens()]
    assert symbols == ["BBB", "AAA"]


def test_legacy_default_file_warns_and_migrates_order(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(cache_path, "Alpha", _token("TKN", "0x0000000000000000000000000000000000000001"))
    _write_tokenlist(cache_path, "Beta", _token("TKN", "0x0000000000000000000000000000000000000002"))
    cache_path.joinpath(".default").write_text("Beta")

    with pytest.warns(FutureWarning, match="legacy `.default` tokenlist file is deprecated"):
        manager = TokenListManager()

    assert cache_path.joinpath(".default").exists()
    assert manager.available_tokenlists() == ["Beta", "Alpha"]
    assert manager.get_token_info("TKN").address == "0x0000000000000000000000000000000000000002"


def _write_tokenlist(cache_path, name, token):
    cache_path.joinpath(f"{name}.json").write_text(
        json.dumps(
            {
                "name": name,
                "timestamp": "2024-01-01T00:00:00Z",
                "version": {"major": 1, "minor": 0, "patch": 0},
                "tokens": [token],
            }
        )
    )


def _token(symbol, address):
    return {
        "chainId": 1,
        "address": address,
        "name": symbol,
        "decimals": 18,
        "symbol": symbol,
    }
