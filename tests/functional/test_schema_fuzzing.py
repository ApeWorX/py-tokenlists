import pytest
import requests  # type: ignore[import]
from hypothesis import HealthCheck, given, settings
from hypothesis_jsonschema import from_schema
from pydantic import ValidationError

from tokenlists import TokenList

TOKENLISTS_SCHEMA = "https://uniswap.org/tokenlist.schema.json"


def clean_data(tl: dict) -> dict:
    # NOTE: Timestamps can be in any format, and our processing handles it okay
    #       However, for testing purposes, we want the output format to line up,
    #       and unfortunately there is some ambiguity in ISO timestamp formats.
    tl["timestamp"] = tl["timestamp"].replace("Z", "+00:00")

    # NOTE: We do not implement `tokenMap` schema version yet
    if "tokenMap" in tl:
        del tl["tokenMap"]

    return tl


@pytest.mark.fuzzing
@given(token_list=from_schema(requests.get(TOKENLISTS_SCHEMA).json()))
@settings(suppress_health_check=(HealthCheck.too_slow,))
def test_schema(token_list):
    try:
        assert TokenList.parse_obj(token_list).dict() == clean_data(token_list)

    except (ValidationError, ValueError):
        pass  # Expect these kinds of errors
