from datetime import datetime
from itertools import chain
from typing import Dict, List, Optional

from pydantic import AnyUrl
from pydantic import BaseModel as _BaseModel
from pydantic import validator
from semantic_version import Version  # type: ignore

ChainId = int

TagId = str

TokenAddress = str
TokenName = str
TokenDecimals = int
TokenSymbol = str


class BaseModel(_BaseModel):
    def dict(self, *args, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True

        return super().dict(*args, **kwargs)

    class Config:
        froze = True


class TokenInfo(BaseModel):
    chainId: ChainId
    address: TokenAddress
    name: TokenName
    decimals: TokenDecimals
    symbol: TokenSymbol
    logoURI: Optional[AnyUrl] = None
    tags: Optional[List[TagId]] = None
    extensions: Optional[dict] = None

    @validator("address")
    def address_must_hex(cls, v: str):
        if not v.startswith("0x") or set(v) > set("x0123456789abcdefABCDEF") or len(v) % 2 != 0:
            raise ValueError("Address is not hex")

        address_bytes = bytes.fromhex(v[2:])  # NOTE: Skip `0x`

        if len(address_bytes) != 20:
            raise ValueError("Address is incorrect length")

        return v

    @validator("decimals")
    def decimals_must_be_uint8(cls, v: TokenDecimals):
        if not (0 <= v < 256):
            raise ValueError(f"Invalid token decimals: {v}")

        return v

    @validator("extensions")
    def extensions_must_contain_simple_types(cls, d: Optional[dict]) -> Optional[dict]:
        if not d:
            return d

        # `extensions` is `Dict[str, Union[str, int, bool, None]]`, but pydantic mutates entries
        for val in d.values():
            if not isinstance(val, (str, int, bool)) and val is not None:
                raise ValueError(f"Incorrect extension field value: {val}")

        return d


class Tag(BaseModel):
    name: str
    description: str


class TokenListVersion(BaseModel, Version):
    major: int
    minor: int
    patch: int

    @validator("*")
    def no_negative_version_numbers(cls, v: int):
        if v < 0:
            raise ValueError("Invalid version number")

        return v

    # NOTE: These properties are just here so that we can use `Version` properly
    @property
    def prerelease(self):
        return None

    @property
    def build(self):
        return None

    def __str__(self) -> str:
        # NOTE: This custom string function is necessary because
        #       `super(Version, self).__str__()` isn't working right
        return f"{self.major}.{self.minor}.{self.patch}"


class TokenList(BaseModel):
    name: str
    timestamp: datetime
    version: TokenListVersion
    tokens: List[TokenInfo]
    keywords: Optional[List[str]] = None
    tags: Optional[Dict[TagId, Tag]] = None
    logoURI: Optional[AnyUrl] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pull all the tags from all the tokens, reference or not
        all_tags = chain.from_iterable(
            list(token.tags) if token.tags else [] for token in self.tokens
        )
        # Obtain the set of all enumerated reference tags e.g. "1", "2", etc.
        token_ref_tags = set(tag for tag in set(all_tags) if set(tag) < set("0123456789"))

        # Compare the enumerated reference tags from the tokens to the tag set in this class
        tokenlist_tags = set(iter(self.tags)) if self.tags else set()
        if token_ref_tags > tokenlist_tags:
            # We have an enumerated reference tag used by a token
            # missing from the our set of tags here
            raise ValueError(
                f"Missing reference tags in tokenlist: {token_ref_tags - tokenlist_tags}"
            )

    class Config:
        # NOTE: Not frozen as we may need to dynamically modify this
        froze = False

    def dict(self, *args, **kwargs) -> dict:
        data = super().dict(*args, **kwargs)
        # NOTE: This was the easiest way to make sure this property returns isoformat
        data["timestamp"] = self.timestamp.isoformat()
        return data
