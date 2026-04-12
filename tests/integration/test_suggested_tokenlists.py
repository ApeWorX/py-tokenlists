import pytest

from tokenlists import TokenListManager, config


@pytest.mark.parametrize("uri", list(config.get_suggested_tokenlists()))
def test_suggested_tokenlists_install(uri, tmp_path, monkeypatch):
    cache_path = tmp_path.joinpath("cache")
    cache_path.mkdir()
    monkeypatch.setattr(config, "DEFAULT_CACHE_PATH", cache_path)
    monkeypatch.chdir(tmp_path)

    manager = TokenListManager()
    installed_name = manager.install_tokenlist(uri)

    assert installed_name in manager.available_tokenlists()
    assert cache_path.joinpath(f"{installed_name}.json").exists()
