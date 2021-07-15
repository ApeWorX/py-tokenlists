import os

import github
import pytest  # type: ignore
import requests  # type: ignore

from tokenlists import TokenList

# NOTE: Must export GITHUB_ACCESS_TOKEN
UNISWAP_REPO = github.Github(os.environ["GITHUB_ACCESS_TOKEN"]).get_repo("Uniswap/token-lists")

UNISWAP_RAW_URL = "https://raw.githubusercontent.com/Uniswap/token-lists/master/test/schema/"


@pytest.mark.parametrize(
    "token_list_file",
    UNISWAP_REPO.get_contents("test/schema"),  # type: ignore
)
def test_uniswap_tokenlists(token_list_file):
    token_list = requests.get(UNISWAP_RAW_URL + token_list_file.name).json()
    assert TokenList.from_dict(token_list).to_dict() == token_list
