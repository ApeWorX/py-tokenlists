import os

import github
import pytest
import requests  # type: ignore[import]
from pydantic import ValidationError

from tokenlists import TokenList

# NOTE: Must export GITHUB_ACCESS_TOKEN
UNISWAP_REPO = github.Github(auth=github.Auth.Token(os.environ["GITHUB_ACCESS_TOKEN"])).get_repo(
    "Uniswap/token-lists"
)

UNISWAP_RAW_URL = "https://raw.githubusercontent.com/Uniswap/token-lists/master/test/schema/"


@pytest.mark.parametrize(
    "token_list_name",
    [f.name for f in UNISWAP_REPO.get_contents("test/schema")],  # type: ignore
)
def test_uniswap_tokenlists(token_list_name):
    token_list = requests.get(UNISWAP_RAW_URL + token_list_name).json()

    if token_list_name == "example.tokenlist.json":
        # NOTE: No idea why this breaking change was necessary
        #       https://github.com/Uniswap/token-lists/pull/420
        token_list.pop("tokenMap")

    if "invalid" not in token_list_name:
        assert TokenList.parse_obj(token_list).dict() == token_list

    else:
        with pytest.raises((ValidationError, ValueError)):
            TokenList.parse_obj(token_list).dict()
