TEST_URI = "tokens.1inch.eth"


def test_empty_list(runner, cli):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output


def test_install(runner, cli):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output

    result = runner.invoke(cli, ["install", TEST_URI])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "1inch" in result.output


def test_remove(runner, cli):
    result = runner.invoke(cli, ["install", TEST_URI])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "1inch" in result.output

    result = runner.invoke(cli, ["remove", "1inch"])
    assert result.exit_code == 0
    assert result.exit_code == 0

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No tokenlists exist" in result.output
