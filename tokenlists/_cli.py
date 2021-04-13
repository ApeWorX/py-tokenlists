import click
import yaml

import tokenlists


@click.group()
def cli():
    """
    Utility for working with the `py-tokenlists` installed token lists
    """


@cli.command(short_help="Display the names and versions of all installed tokenlists")
def show_lists():
    click.echo("Installed Token Lists:")
    for token_list in map(tokenlists.get_token_list, tokenlists.available_token_lists()):
        click.echo(f"- {token_list.name} (v{token_list.version})")


@cli.command(short_help="Display the info for a particular token")
@click.argument("symbol", type=tokenlists.typing.TokenSymbol)
@click.option(
    "--token-list",
    type=click.Choice(tokenlists.available_token_lists()),
    default=tokenlists.default_token_list(),
)
def token_info(symbol, token_list):
    token_info = tokenlists.get_token_info(symbol, token_list)
    click.echo(yaml.dump(token_info.to_dict()))


@cli.command(short_help="Install a new token list")
@click.argument("uri")
def install(uri):
    tokenlists.install_token_list(uri)


@cli.command(short_help="Remove an existing token list")
@click.argument("name", type=click.Choice(tokenlists.available_token_lists()))
def remove(name):
    tokenlists.uninstall_token_list(name)


@cli.command(short_help="Set the default tokenlist")
@click.argument("name", type=click.Choice(tokenlists.available_token_lists()))
def set_default(name):
    tokenlists.set_default_token_list(name)
