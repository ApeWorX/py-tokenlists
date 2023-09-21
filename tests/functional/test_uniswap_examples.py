import os
from typing import Any, Optional

import github
import pytest
import requests
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

    if "invalid" in token_list_name:
        with pytest.raises((ValidationError, ValueError)):
            TokenList.model_validate(token_list)
    else:
        actual = TokenList.model_validate(token_list).model_dump(mode="json")

        def assert_tokenlists(_actual: Any, _expected: Any, parent_key: Optional[str] = None):
            parent_key = parent_key or "__root__"
            assert type(_actual) is type(_expected)

            if isinstance(_actual, list):
                for idx, (actual_item, expected_item) in enumerate(zip(_actual, _expected)):
                    assert_tokenlists(
                        actual_item, expected_item, parent_key=f"{parent_key}_index_{idx}"
                    )

            elif isinstance(_actual, dict):
                unexpected = {}
                handled = set()
                for key, actual_value in _actual.items():
                    if key not in _expected:
                        unexpected[key] = actual_value
                        continue

                    expected_value = _expected[key]
                    assert type(actual_value) is type(expected_value)
                    assert_tokenlists(actual_value, expected_value, parent_key=key)
                    handled.add(key)

                handled_str = ", ".join(list(handled)) or "<Nothing handled>"
                missing = {f"{x}" for x in _expected if x not in handled}
                unexpected_str = ", ".join([f"{k}={v}" for k, v in unexpected.items()])
                assert not unexpected, f"Unexpected keys: {unexpected_str}, Parent: {parent_key}"
                assert not missing, (
                    f"Missing keys: '{', '.join(list(missing))}'; "
                    f"handled: '{handled_str}', "
                    f"Parent: {parent_key}."
                )

            else:
                assert _actual == _expected

        assert_tokenlists(actual, token_list)
