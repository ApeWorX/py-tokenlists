# TODO: Seems like Click 8.1.5 introduced this
# mypy: disable-error-code=attr-defined
import re

import click

from .manager import TokenListManager
from .typing import TokenSymbol


class TokenlistChoice(click.Choice):
    def __init__(self, case_sensitive=True):
        self.case_sensitive = case_sensitive

    @property
    def choices(self):
        return list(TokenListManager().available_tokenlists())


@click.group(short_help="Work with token lists")
@click.version_option(message="%(version)s", package_name="tokenlists")
def cli():
    """
    Utility for working with the `py-tokenlists` installed token lists
    """


@cli.command(name="list", short_help="Display the names and versions of all installed tokenlists")
def _list():
    manager = TokenListManager()

    available_tokenlists = manager.available_tokenlists()
    if available_tokenlists:
        click.echo("Installed Token Lists:")
        for tokenlist in map(manager.get_tokenlist, available_tokenlists):
            click.echo(f"- {tokenlist.name} (v{tokenlist.version})")

    else:
        click.echo("WARNING: No tokenlists exist!")


@cli.command(short_help="Install a new tokenlist")
@click.argument("uri")
def install(uri):
    manager = TokenListManager()
    manager.install_tokenlist(uri)


@cli.command(short_help="Remove an existing tokenlist")
@click.argument("name", type=TokenlistChoice())
def remove(name):
    manager = TokenListManager()
    manager.remove_tokenlist(name)


@cli.command(short_help="Set the default tokenlist")
@click.argument("name", type=TokenlistChoice())
def set_default(name):
    manager = TokenListManager()
    manager.set_default_tokenlist(name)
    click.echo(f"Default tokenlist is now: '{manager.default_tokenlist}'")


@cli.command(short_help="Display the names and versions of all installed tokenlists")
@click.option("--search", default="")
@click.option("--tokenlist-name", type=TokenlistChoice(), default=None)
@click.option("--chain-id", default=1, type=int)
def list_tokens(search, tokenlist_name, chain_id):
    manager = TokenListManager()

    if not manager.default_tokenlist:
        raise click.ClickException("No tokenlists available!")

    pattern = re.compile(search or ".*")

    for token_info in filter(
        lambda t: pattern.match(t.symbol),
        manager.get_tokens(tokenlist_name, chain_id),
    ):
        click.echo("{address} ({symbol})".format(**token_info.model_dump(mode="json")))


@cli.command(short_help="Display the info for a particular token")
@click.argument("symbol", type=TokenSymbol)
@click.option("--tokenlist-name", type=TokenlistChoice(), default=None)
@click.option("--case-insensitive", default=False, is_flag=True)
@click.option("--chain-id", default=1, type=int)
def token_info(symbol, tokenlist_name, chain_id, case_insensitive):
    manager = TokenListManager()

    if not manager.default_tokenlist:
        raise click.ClickException("No tokenlists available!")

    token_info = manager.get_token_info(symbol, tokenlist_name, chain_id, case_insensitive)
    token_info = token_info.model_dump(mode="json")

    if "tags" not in token_info:
        token_info["tags"] = ""

    click.echo(
        """
      Symbol: {symbol}
        Name: {name}
    Chain ID: {chainId}
     Address: {address}
    Decimals: {decimals}
        Tags: {tags}
    """.format(
            **token_info
        )
    )
