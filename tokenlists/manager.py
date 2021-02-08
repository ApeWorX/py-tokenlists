import json
from typing import Dict, List

import requests

from tokenlists import config
from tokenlists.typing import ChainId, TokenInfo, TokenList, TokenSymbol

INSTALLED_TOKEN_LISTS: Dict[str, TokenList] = {}


def _load_token_lists():
    config.DATA_FOLDER.mkdir(exist_ok=True)

    for path in config.DATA_FOLDER.glob("*.json"):
        with path.open() as fp:
            token_list = TokenList.from_dict(json.load(fp))
            INSTALLED_TOKEN_LISTS[token_list.name] = token_list


def install_token_list(uri: str) -> None:
    if uri.endswith(".eth"):
        uri = config.UNISWAP_ENS_TOKENLISTS_HOST.format(uri)

    token_list = TokenList.from_dict(requests.get(uri).json())

    _load_token_lists()
    INSTALLED_TOKEN_LISTS[token_list.name] = token_list

    token_list_file = config.DATA_FOLDER.joinpath(f"{token_list.name}.json")
    with token_list_file.open("w") as fp:
        json.dump(token_list.to_dict(), fp)


def uninstall_token_list(token_list_name: str = "") -> None:
    token_list = get_token_list(token_list_name)

    if token_list.name == config.DEFAULT_TOKEN_LIST:
        config.DEFAULT_TOKEN_LIST = None

    token_list_file = config.DATA_FOLDER.joinpath(f"{token_list.name}.json")
    token_list_file.unlink()

    del INSTALLED_TOKEN_LISTS[token_list.name]


def set_default_token_list(name: str) -> None:
    _load_token_lists()
    if name not in INSTALLED_TOKEN_LISTS:
        raise ValueError(f"Unknown token list: {name}")

    config.DEFAULT_TOKEN_LIST = name


def available_token_lists() -> List[str]:
    _load_token_lists()
    return sorted(INSTALLED_TOKEN_LISTS)


def get_token_list(token_list_name: str = "") -> TokenList:
    if not token_list_name:
        if config.DEFAULT_TOKEN_LIST is None:
            raise ValueError("Default token list has not been set.")
        token_list_name = config.DEFAULT_TOKEN_LIST

    _load_token_lists()
    if token_list_name not in INSTALLED_TOKEN_LISTS:
        raise ValueError(f"Unknown token list: {token_list_name}")

    return INSTALLED_TOKEN_LISTS[token_list_name]


def get_token_info(
    symbol: TokenSymbol,
    token_list_name: str = "",
    chain_id: ChainId = 1,
) -> TokenInfo:
    token_list = get_token_list(token_list_name)

    matching_tokens = [
        token
        for token in token_list.tokens
        if (token.symbol == symbol and token.chainId == chain_id)
    ]

    if len(matching_tokens) == 0:
        raise ValueError(
            f"Token with symbol '{symbol}' does not exist" f" within '{token_list}' token list."
        )

    elif len(matching_tokens) > 1:
        raise ValueError(
            f"Multiple tokens with symbol '{symbol}'" f" found in '{token_list}' token list."
        )

    else:
        return matching_tokens[0]
