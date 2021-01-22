import json
from typing import List

import requests
from brownie import Contract, chain
from brownie._config import DATA_FOLDER

DEFAULT_TOKEN_LIST = None
TOKEN_LISTS = {}


DATA_FOLDER.joinpath("tokenlists").mkdir(exist_ok=True)
for path in DATA_FOLDER.glob("tokenlists/*.json"):
    with path.open() as fp:
        data = json.load(fp)
        TOKEN_LISTS[data["name"]] = data["tokens"]


def fetch_token_list(uri: str) -> None:
    if uri.endswith(".eth"):
        uri = f"https://wispy-bird-88a7.uniswap.workers.dev/?url=http://{uri}.link"
    data = requests.get(uri).json()
    name = data["name"]
    TOKEN_LISTS[name] = data["tokens"]
    with DATA_FOLDER.joinpath(f"tokenlists/{name}.json").open("w") as fp:
        json.dump(data, fp)


def set_default_token_list(name: str) -> None:
    if name not in TOKEN_LISTS:
        raise ValueError(f"Unknown token list: {name}")
    global DEFAULT_TOKEN_LIST
    DEFAULT_TOKEN_LIST = name


def get_available_token_lists() -> List[str]:
    return sorted(TOKEN_LISTS)


def get_token(symbol: str, token_list: str = None) -> Contract:
    if token_list is None:
        if DEFAULT_TOKEN_LIST is None:
            raise ValueError("Default token list has not been set.")
        token_list = DEFAULT_TOKEN_LIST
    symbol = symbol.lower()
    token_data = TOKEN_LISTS[token_list]
    data = [
        i
        for i in token_data
        if symbol == i["symbol"].lower() and i["chainId"] == chain.id
    ]
    if not data:
        raise ValueError(f"Symbol does not exist within '{token_list}' token list.")
    if len(data) > 1:
        raise ValueError(
            f"Multiple tokens within '{token_list}' token list using this symbol."
        )
    address = data[0]["address"]
    try:
        return Contract(address)
    except ValueError:
        return Contract.from_explorer(address)
