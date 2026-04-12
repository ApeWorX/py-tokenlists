import json

import pytest

from tokenlists import TokenListManager, config


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

    _write_tokenlist(
        cache_path, "Alpha", _token("TKN", "0x0000000000000000000000000000000000000001")
    )
    _write_tokenlist(
        cache_path, "Beta", _token("TKN", "0x0000000000000000000000000000000000000002")
    )

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

    _write_tokenlist(
        cache_path, "Alpha", _token("AAA", "0x0000000000000000000000000000000000000001")
    )
    _write_tokenlist(
        cache_path, "Beta", _token("BBB", "0x0000000000000000000000000000000000000002")
    )

    symbols = [token.symbol for token in TokenListManager().get_tokens()]
    assert symbols == ["BBB", "AAA"]


def test_get_token_info_defaults_to_any_chain(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(
        cache_path,
        "Alpha",
        _token("TKN", "0x0000000000000000000000000000000000000001", chain_id=137),
    )

    token_info = TokenListManager().get_token_info("TKN")
    assert token_info.chainId == 137


def test_get_tokens_with_chain_id_none_returns_all_chains(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(
        cache_path,
        "Alpha",
        _token("AAA", "0x0000000000000000000000000000000000000001", chain_id=1),
        _token("BBB", "0x0000000000000000000000000000000000000002", chain_id=10),
    )

    chain_ids = [token.chainId for token in TokenListManager().get_tokens(chain_id=None)]
    assert chain_ids == [1, 10]


def test_get_token_info_supports_base58_addresses(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(
        cache_path,
        "Alpha",
        _token("MICHI", "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp", chain_id=501000101),
    )

    token_info = TokenListManager().get_token_info("MICHI")
    assert token_info.address == "5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp"
    assert token_info.chainId == 501000101


def test_legacy_default_file_warns_and_migrates_order(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(
        cache_path, "Alpha", _token("TKN", "0x0000000000000000000000000000000000000001")
    )
    _write_tokenlist(
        cache_path, "Beta", _token("TKN", "0x0000000000000000000000000000000000000002")
    )
    cache_path.joinpath(".default").write_text("Beta")

    with pytest.warns(FutureWarning, match="legacy `.default` tokenlist file is deprecated"):
        manager = TokenListManager()

    assert cache_path.joinpath(".default").exists()
    assert manager.available_tokenlists() == ["Beta", "Alpha"]
    assert manager.get_token_info("TKN").address == "0x0000000000000000000000000000000000000002"


def test_install_persists_resolved_source_url(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    class FakeResponse:
        text = ""
        url = "https://example.com/tokenlist.json"

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "name": "Alpha",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": {"major": 1, "minor": 0, "patch": 0},
                "tokens": [_token("AAA", "0x0000000000000000000000000000000000000001")],
            }

    requested = {}

    def fake_get(uri, **kwargs):
        requested["uri"] = uri
        requested["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr("tokenlists.manager.httpx.get", fake_get)

    TokenListManager().install_tokenlist("https://example.com/install.json")

    cached = json.loads(cache_path.joinpath("Alpha.json").read_text())
    assert cached["tokenlistsSourceUrl"] == "https://example.com/tokenlist.json"
    assert requested["uri"] == "https://example.com/install.json"
    assert requested["kwargs"]["follow_redirects"] is True


def test_update_tokenlist_uses_stored_source_url(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(
        cache_path,
        "Alpha",
        _token("AAA", "0x0000000000000000000000000000000000000001"),
        tokenlistsSourceUrl="https://example.com/tokenlist.json",
    )

    class FakeResponse:
        text = ""
        url = "https://cdn.example.com/tokenlist.json"

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "name": "Alpha",
                "timestamp": "2024-01-02T00:00:00Z",
                "version": {"major": 1, "minor": 1, "patch": 0},
                "tokens": [_token("BBB", "0x0000000000000000000000000000000000000002")],
            }

    called_uris = []

    def fake_get(uri, **kwargs):
        called_uris.append(uri)
        assert kwargs["follow_redirects"] is True
        return FakeResponse()

    monkeypatch.setattr("tokenlists.manager.httpx.get", fake_get)

    updated_name = TokenListManager().update_tokenlist("Alpha")

    assert updated_name == "Alpha"
    assert called_uris == ["https://example.com/tokenlist.json"]
    cached = json.loads(cache_path.joinpath("Alpha.json").read_text())
    assert cached["version"] == {"major": 1, "minor": 1, "patch": 0}
    assert cached["tokenlistsSourceUrl"] == "https://cdn.example.com/tokenlist.json"


def test_update_tokenlist_without_stored_source_url_returns_none(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    _write_tokenlist(
        cache_path, "Alpha", _token("AAA", "0x0000000000000000000000000000000000000001")
    )

    assert TokenListManager().update_tokenlist("Alpha") is None


def test_install_writes_utf8_cache_file(tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    class FakeResponse:
        text = ""
        url = "https://example.com/tokenlist.json"

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "name": "Alpha",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": {"major": 1, "minor": 0, "patch": 0},
                "tokens": [
                    {
                        **_token("A\u0361LPHA", "0x0000000000000000000000000000000000000001"),
                        "name": "Optimism \u0361 Token",
                    }
                ],
            }

    monkeypatch.setattr("tokenlists.manager.httpx.get", lambda *args, **kwargs: FakeResponse())

    TokenListManager().install_tokenlist("https://example.com/install.json")

    cached = cache_path.joinpath("Alpha.json").read_text(encoding="utf-8")
    assert "A\u0361LPHA" in cached


def _write_tokenlist(cache_path, name, *tokens, **extra_data):
    cache_path.joinpath(f"{name}.json").write_text(
        json.dumps(
            {
                "name": name,
                "timestamp": "2024-01-01T00:00:00Z",
                "version": {"major": 1, "minor": 0, "patch": 0},
                "tokens": list(tokens),
                **extra_data,
            }
        ),
        encoding="utf-8",
    )


def _token(symbol, address, chain_id=1):
    return {
        "chainId": chain_id,
        "address": address,
        "name": symbol,
        "decimals": 18,
        "symbol": symbol,
    }
