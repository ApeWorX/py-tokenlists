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


def test_install(runner, cli):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output

    result = runner.invoke(cli, ["install", TEST_URI])
    assert result.exit_code == 0, result.output

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "1inch" in result.output


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
