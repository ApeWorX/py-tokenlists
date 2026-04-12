import json
from pathlib import Path

from tokenlists import __main__ as cli_module
from tokenlists.version import version

TEST_URI = "tokens.1inch.eth"


def test_version(runner, cli):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version


def test_empty_list(runner, cli):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output
    assert "tokenlists suggestions" in result.output


def test_suggestions(runner, cli):
    result = runner.invoke(cli, ["suggestions"])
    assert result.exit_code == 0
    assert "Suggested Token Lists:" in result.output
    assert "Uniswap Default List" in result.output
    assert "https://ipfs.io/ipns/tokens.uniswap.org" in result.output


def test_install(runner, cli):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output

    result = runner.invoke(cli, ["install", TEST_URI])
    assert result.exit_code == 0, result.output

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "1inch" in result.output


def test_new_writes_empty_tokenlist_to_selected_path(runner, cli):
    result = runner.invoke(
        cli,
        [
            "new",
            "custom/tokenlist.json",
            "--name",
            "My Token List",
            "--keyword",
            "stablecoin",
            "--keyword",
            "dex",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "custom/tokenlist.json" in result.output

    written = json.loads(Path("custom/tokenlist.json").read_text(encoding="utf-8"))
    assert written["name"] == "My Token List"
    assert written["tokens"] == []
    assert written["version"] == {"major": 1, "minor": 0, "patch": 0}
    assert written["keywords"] == ["stablecoin", "dex"]


def test_add_updates_local_tokenlist_and_bumps_minor_version(runner, cli):
    Path("tokenlist.json").write_text(
        json.dumps(
            {
                "name": "My Token List",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": {"major": 1, "minor": 0, "patch": 0},
                "tokens": [],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli,
        [
            "add",
            "tokenlist.json",
            "--chain-id",
            "1",
            "--address",
            "0x0000000000000000000000000000000000000001",
            "--name",
            "Token",
            "--symbol",
            "TKN",
            "--decimals",
            "18",
            "--tag",
            "stablecoin",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "v1.1.0" in result.output

    written = json.loads(Path("tokenlist.json").read_text(encoding="utf-8"))
    assert written["version"] == {"major": 1, "minor": 1, "patch": 0}
    assert written["tokens"][0]["symbol"] == "TKN"
    assert written["tokens"][0]["tags"] == ["stablecoin"]


def test_install_from_local_path(runner, cli):
    Path("tokenlist.json").write_text(
        json.dumps(
            {
                "name": "Local List",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": {"major": 1, "minor": 0, "patch": 0},
                "tokens": [
                    {
                        "chainId": 1,
                        "address": "0x0000000000000000000000000000000000000001",
                        "name": "Token",
                        "decimals": 18,
                        "symbol": "TKN",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(cli, ["install", "tokenlist.json"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Local List" in result.output


def test_remove(runner, cli):
    result = runner.invoke(cli, ["install", TEST_URI])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "1inch" in result.output

    result = runner.invoke(cli, ["remove", "1inch default token list"])
    assert result.exit_code == 0
    assert result.exit_code == 0

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output


def test_set_default_removed(runner, cli):
    result = runner.invoke(cli, ["set-default", "1inch default token list"])
    assert result.exit_code != 0
    assert "No such command 'set-default'" in result.output


def test_token_info_displays_tokenlist_name(runner, cli, monkeypatch):
    class FakeTokenInfo:
        def model_dump(self, mode="json"):
            return {
                "symbol": "TKN",
                "name": "Token",
                "chainId": 137,
                "address": "0x0000000000000000000000000000000000000001",
                "decimals": 18,
                "tags": [],
            }

    class FakeManager:
        def available_tokenlists(self):
            return ["Preferred List"]

        def get_token_info_with_tokenlist(self, symbol, tokenlist_name, chain_id, case_insensitive):
            return "Preferred List", FakeTokenInfo()

    monkeypatch.setattr(cli_module, "TokenListManager", FakeManager)

    result = runner.invoke(cli, ["token-info", "TKN"])
    assert result.exit_code == 0
    assert "Token List: Preferred List" in result.output


def test_update_warns_when_source_url_missing(runner, cli, monkeypatch):
    class FakeManager:
        def available_tokenlists(self):
            return ["Preferred List"]

        def update_tokenlist(self, tokenlist_name):
            return None

    monkeypatch.setattr(cli_module, "TokenListManager", FakeManager)

    result = runner.invoke(cli, ["update", "Preferred List"])
    assert result.exit_code == 0
    assert "does not have a stored source URL and cannot be updated" in result.output


def test_update_all_updates_each_list(runner, cli, monkeypatch):
    updated = []

    class FakeManager:
        def available_tokenlists(self):
            return ["Alpha", "Beta"]

        def update_tokenlist(self, tokenlist_name):
            updated.append(tokenlist_name)
            return tokenlist_name

    monkeypatch.setattr(cli_module, "TokenListManager", FakeManager)

    result = runner.invoke(cli, ["update", "--all"])
    assert result.exit_code == 0
    assert updated == ["Alpha", "Beta"]
    assert "Updated 'Alpha'." in result.output
    assert "Updated 'Beta'." in result.output
