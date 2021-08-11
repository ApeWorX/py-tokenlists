import pytest
import requests  # type: ignore
from hypothesis import HealthCheck, given, settings
from hypothesis_jsonschema import from_schema
from pydantic import ValidationError

from tokenlists import TokenList

TOKENLISTS_SCHEMA = "https://uniswap.org/tokenlist.schema.json"


@pytest.mark.fuzzing
@given(token_list=from_schema(requests.get(TOKENLISTS_SCHEMA).json()))
@settings(suppress_health_check=(HealthCheck.too_slow,))
def test_schema(token_list):
    try:
        assert TokenList.parse_obj(token_list).dict() == token_list

    except (ValidationError, ValueError):
        pass  # Expect these kinds of errors
