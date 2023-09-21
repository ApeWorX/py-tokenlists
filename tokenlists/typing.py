from itertools import chain
from typing import Any, Dict, List, Optional

from pydantic import AnyUrl
from pydantic import BaseModel as _BaseModel
from pydantic import PastDatetime, field_validator

ChainId = int
TagId = str
TokenAddress = str
TokenName = str
TokenDecimals = int
TokenSymbol = str


class BaseModel(_BaseModel):
    def model_dump(self, *args, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True

        return super().model_dump(*args, **kwargs)

    class Config:
        froze = True


class BridgeInfo(BaseModel):
    tokenAddress: TokenAddress
    originBridgeAddress: Optional[TokenAddress] = None
    destBridgeAddress: Optional[TokenAddress] = None


class TokenInfo(BaseModel):
    chainId: ChainId
    address: TokenAddress
    name: TokenName
    decimals: TokenDecimals
    symbol: TokenSymbol
    logoURI: Optional[str] = None
    tags: Optional[List[TagId]] = None
    extensions: Optional[Dict[str, Any]] = None

    @field_validator("logoURI")
    def validate_uri(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if "://" not in v or not AnyUrl(v):
            raise ValueError(f"'{v}' is not a valid URI")

        return v

    @field_validator("extensions", mode="before")
    def parse_extensions(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        # 1. Check extension depth first
        def extension_depth(obj: Optional[Dict[str, Any]]) -> int:
            if not isinstance(obj, dict) or len(obj) == 0:
                return 0

            return 1 + max(extension_depth(v) for v in obj.values())

        if (depth := extension_depth(v)) > 3:
            raise ValueError(f"Extension depth is greater than 3: {depth}")

        # 2. Parse valid extensions
        if v and "bridgeInfo" in v:
            # NOTE: Avoid modifying `v`.
            return {
                **v,
                "bridgeInfo": {
                    int(k): BridgeInfo.model_validate(v) for k, v in v["bridgeInfo"].items()
                },
            }

        return v

    @field_validator("extensions")
    def extensions_must_contain_allowed_types(
        cls, d: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if not d:
            return d

        # NOTE: `extensions` is mapping from `str` to either:
        #       - a parsed `dict` type (e.g. `BaseModel`)
        #       - a "simple" type (e.g. dict, string, integer or boolean value)
        for key, val in d.items():
            if val is not None and not isinstance(val, (BaseModel, str, int, bool, dict)):
                raise ValueError(f"Incorrect extension field value: {val}")

        return d

    @property
    def bridge_info(self) -> Optional[BridgeInfo]:
        if self.extensions and "bridgeInfo" in self.extensions:
            return self.extensions["bridgeInfo"]

        return None

    @field_validator("address")
    def address_must_hex(cls, v: str):
        if not v.startswith("0x") or set(v) > set("x0123456789abcdefABCDEF") or len(v) % 2 != 0:
            raise ValueError("Address is not hex")

        address_bytes = bytes.fromhex(v[2:])  # NOTE: Skip `0x`

        if len(address_bytes) != 20:
            raise ValueError("Address is incorrect length")

        return v

    @field_validator("decimals")
    def decimals_must_be_uint8(cls, v: TokenDecimals):
        if not (0 <= v < 256):
            raise ValueError(f"Invalid token decimals: {v}")

        return v


class Tag(BaseModel):
    name: str
    description: str


class TokenListVersion(BaseModel):
    major: int
    minor: int
    patch: int

    @field_validator("*")
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
    timestamp: PastDatetime
    version: TokenListVersion
    tokens: List[TokenInfo]
    keywords: Optional[List[str]] = None
    tags: Optional[Dict[TagId, Tag]] = None
    logoURI: Optional[str] = None

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

    @field_validator("logoURI")
    def validate_uri(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if "://" not in v or not AnyUrl(v):
            raise ValueError(f"'{v}' is not a valid URI")

        return v

    def model_dump(self, *args, **kwargs) -> Dict:
        data = super().model_dump(*args, **kwargs)

        if kwargs.get("mode", "").lower() == "json":
            # NOTE: This was the easiest way to make sure this property returns isoformat
            data["timestamp"] = self.timestamp.isoformat()

        return data
