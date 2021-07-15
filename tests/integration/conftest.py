from pathlib import Path

import pytest  # type: ignore
from click.testing import CliRunner

from tokenlists import TokenListManager, _cli


@pytest.fixture
def runner(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem() as temp_dir:
        monkeypatch.setattr(_cli, "TokenListManager", lambda: TokenListManager(Path(temp_dir)))
        yield runner


@pytest.fixture
def cli(runner):
    # NOTE: Depends on `runner` fixture for config side effects
    yield _cli.cli
