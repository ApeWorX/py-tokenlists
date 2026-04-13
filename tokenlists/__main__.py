# TODO: Seems like Click 8.1.5 introduced this
# mypy: disable-error-code=attr-defined
import re
from pathlib import Path

import click

from . import config
from .manager import TokenListManager
from .typing import TokenInfo, TokenList, TokenSymbol


class TokenlistChoice(click.Choice):
    def __init__(self, case_sensitive=True):
        self.case_sensitive = case_sensitive

    @property
    def choices(self):
        return list(TokenListManager().available_tokenlists())


@click.group()
@click.version_option(message="%(version)s", package_name="tokenlists")
def cli():
    """
    Work with Tokenlists (https://tokenlists.org)
    """


@cli.group()
def cache():
    """Manage Tokenlist cache"""


@cache.command(name="list")
@click.option("--suggested", "show_suggested", is_flag=True)
def list_installed(show_suggested):
    """Display the names and versions of all installed tokenlists"""

    manager = TokenListManager()

    if show_suggested:
        click.echo("Suggested Token Lists:")
        for uri, metadata in config.get_suggested_tokenlists().items():
            click.echo(f"  {metadata['name']}:")

            if homepage := metadata.get("homepage"):
                click.echo(f"    hompage: {homepage}")

            click.echo(f"    uri: {uri}")

    elif installed_tokenlists := manager.available_tokenlists():
        click.echo("Installed Token Lists:")
        for tokenlist in map(manager.get_tokenlist, installed_tokenlists):
            click.echo(f"- {tokenlist.name} (v{tokenlist.version})")

    else:
        click.echo(
            "WARNING: No tokenlists exist! "
            "Run `tokenlists suggestions` to browse installable lists."
        )


@cache.command()
@click.argument("uri")
def add(uri):
    """Install a tokenlist from a URI, ENS name, or local JSON file"""

    manager = TokenListManager()
    manager.install_tokenlist(uri)


@cache.command()
@click.argument("name", type=TokenlistChoice(), required=False)
@click.option("--all", "update_all", default=False, is_flag=True)
def refresh(name, update_all):
    """Update installed tokenlist(s) from their stored source URLs"""

    manager = TokenListManager()

    if not manager.available_tokenlists():
        raise click.ClickException("No tokenlists available!")

    if update_all == bool(name):
        raise click.ClickException("Provide either a tokenlist name or `--all`.")

    tokenlist_names = manager.available_tokenlists() if update_all else [name]
    for tokenlist_name in tokenlist_names:
        updated_name = manager.update_tokenlist(tokenlist_name)
        if updated_name is None:
            click.echo(
                f"WARNING: Token list '{tokenlist_name}' does not have a stored "
                "source URL and cannot be updated."
            )
        elif updated_name == tokenlist_name:
            click.echo(f"Updated '{tokenlist_name}'.")
        else:
            click.echo(f"Updated '{tokenlist_name}' as '{updated_name}'.")


@cache.command()
@click.argument("name", type=TokenlistChoice())
def clear(name):
    """Remove an existing tokenlist"""

    manager = TokenListManager()
    manager.remove_tokenlist(name)


@cli.group()
def manage():
    """Manage your own custom Tokenlist"""


@manage.command()
@click.argument(
    "path",
    required=False,
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option("--name", default=None)
@click.option("--logo-uri", default=None)
@click.option("--keyword", "keywords", multiple=True)
def new(path, name, logo_uri, keywords):
    """Create a new local tokenlist JSON file"""

    path = path or Path(click.prompt("Output path", default="./tokenlist.json"))
    if path.exists() and not click.confirm(f"{path} already exists. Overwrite it?"):
        raise click.ClickException("Aborted.")

    name = name or click.prompt("Token list name")
    keywords = list(keywords) or None

    tokenlist = TokenList.create_empty(name=name, logo_uri=logo_uri, keywords=keywords)
    tokenlist.save(path)
    click.echo(f"Wrote empty tokenlist to {path}.")


@manage.command(name="add")
@click.argument(
    "path",
    required=False,
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option("--chain-id", type=int, default=None)
@click.option("--address", default=None)
@click.option("--name", default=None)
@click.option("--symbol", default=None)
@click.option("--decimals", type=int, default=None)
@click.option("--logo-uri", default=None)
@click.option("--tag", "tags", multiple=True)
@click.option("--bump-version", type=click.Choice(["major", "minor", "patch"]), default=None)
def add_token(path, chain_id, address, name, symbol, decimals, logo_uri, tags, bump_version):
    """Add a token to an existing local tokenlist JSON file"""

    path = path or Path(click.prompt("Tokenlist path", default="./tokenlist.json"))
    tokenlist = TokenList.load(path)

    token_info = TokenInfo(
        chainId=chain_id if chain_id is not None else click.prompt("Chain ID", type=int),
        address=address or click.prompt("Token address"),
        name=name or click.prompt("Token name"),
        symbol=symbol or click.prompt("Token symbol"),
        decimals=decimals if decimals is not None else click.prompt("Token decimals", type=int),
        logoURI=logo_uri,
        tags=list(tags) or None,
    )

    updated_tokenlist = tokenlist.add_token(token_info)
    if bump_version:
        updated_tokenlist = updated_tokenlist.bump_version(bump_version)

    updated_tokenlist.save(path)
    click.echo(f"Added {token_info.symbol} to {path} (v{updated_tokenlist.version}).")


@cli.command(name="list")
@click.option("--symbol", default=None)
@click.option("--tokenlist", type=TokenlistChoice(), default=None)
@click.option("--chain-id", default=None, type=int)
def list_tokens(symbol, tokenlist, chain_id):
    """List all available tokens, filtered by OPTIONS"""

    manager = TokenListManager()

    if not manager.available_tokenlists():
        raise click.ClickException("No tokenlists available!")

    pattern = re.compile(symbol or ".*")

    for token_info in filter(
        lambda t: pattern.match(t.symbol),
        manager.get_tokens(tokenlist, chain_id),
    ):
        click.echo("{address} ({symbol})".format(**token_info.model_dump(mode="json")))


@cli.command()
@click.argument("symbol", type=TokenSymbol)
@click.option("--tokenlist-name", type=TokenlistChoice(), default=None)
@click.option("--case-insensitive", default=False, is_flag=True)
@click.option("--chain-id", default=None, type=int)
def info(symbol, tokenlist_name, chain_id, case_insensitive):
    """Display the info for a particular token"""

    manager = TokenListManager()

    if not manager.available_tokenlists():
        raise click.ClickException("No tokenlists available!")

    tokenlist_name, token_info = manager.get_token_info_with_tokenlist(
        symbol, tokenlist_name, chain_id, case_insensitive
    )
    token_info = token_info.model_dump(mode="json")
    token_info["tokenlist_name"] = tokenlist_name

    if "tags" not in token_info:
        token_info["tags"] = ""

    click.echo(
        """
      Symbol: {symbol}
        Name: {name}
  Token List: {tokenlist_name}
    Chain ID: {chainId}
     Address: {address}
    Decimals: {decimals}
        Tags: {tags}
    """.format(**token_info)
    )


if __name__ == "__main__":
    cli()
