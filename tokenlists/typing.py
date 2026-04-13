from datetime import datetime, timedelta, timezone
from itertools import chain
from pathlib import Path
from typing import Any, Literal

from pydantic import AnyUrl, ConfigDict, PastDatetime, field_validator
from pydantic import BaseModel as _BaseModel

ChainId = int
TagId = str
TokenAddress = str
TokenName = str
TokenDecimals = int
TokenSymbol = str
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58_CHARACTERS = set(BASE58_ALPHABET)


class BaseModel(_BaseModel):
    def model_dump(self, *args, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True

        return super().model_dump(*args, **kwargs)

    model_config = ConfigDict(frozen=True)


class BridgeInfo(BaseModel):
    tokenAddress: TokenAddress
    originBridgeAddress: TokenAddress | None = None
    destBridgeAddress: TokenAddress | None = None


class TokenInfo(BaseModel):
    chainId: ChainId
    address: TokenAddress
    name: TokenName
    decimals: TokenDecimals
    symbol: TokenSymbol
    logoURI: str | None = None
    tags: list[TagId] | None = None
    extensions: dict[str, Any] | None = None

    @field_validator("logoURI")
    def validate_uri(cls, v: str | None) -> str | None:
        if v is None:
            return v

        if "://" not in v or not AnyUrl(v):
            raise ValueError(f"'{v}' is not a valid URI")

        return v

    @field_validator("extensions", mode="before")
    def parse_extensions(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        # 1. Check extension depth first
        def extension_depth(obj: dict[str, Any] | None) -> int:
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
        cls, d: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        if not d:
            return d

        # NOTE: `extensions` is mapping from `str` to either:
        #       - a parsed `dict` type (e.g. `BaseModel`)
        #       - a "simple" type (e.g. dict, string, integer or boolean value)
        for _key, val in d.items():
            if val is not None and not isinstance(val, (BaseModel, str, int, bool, dict)):
                raise ValueError(f"Incorrect extension field value: {val}")

        return d

    @property
    def bridge_info(self) -> BridgeInfo | None:
        if self.extensions and "bridgeInfo" in self.extensions:
            return self.extensions["bridgeInfo"]

        return None

    @field_validator("address")
    def address_must_be_supported_format(cls, value: str) -> str:
        if value.startswith("0x"):
            return cls._validate_hex_address(value)

        if cls._is_base58_address(value):
            return value

        raise ValueError("Address is not a supported hex or base58 value")

    @classmethod
    def _validate_hex_address(cls, value: str) -> str:
        if set(value) > set("x0123456789abcdefABCDEF") or len(value) % 2 != 0:
            raise ValueError("Address is not hex")

        address_bytes = bytes.fromhex(value[2:])  # NOTE: Skip `0x`
        if len(address_bytes) != 20:
            raise ValueError("Address is incorrect length")

        return value

    @classmethod
    def _is_base58_address(cls, value: str) -> bool:
        if not value or set(value) - BASE58_CHARACTERS:
            return False

        decoded_length = len(cls._decode_base58(value))
        return 1 <= decoded_length <= 64

    @classmethod
    def _decode_base58(cls, value: str) -> bytes:
        integer = 0
        for character in value:
            integer = integer * 58 + BASE58_ALPHABET.index(character)

        decoded = bytearray()
        while integer > 0:
            integer, remainder = divmod(integer, 256)
            decoded.append(remainder)

        decoded.reverse()
        leading_zeroes = len(value) - len(value.lstrip("1"))
        return (b"\x00" * leading_zeroes) + bytes(decoded)

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
    tokens: list[TokenInfo]
    keywords: list[str] | None = None
    tags: dict[TagId, Tag] | None = None
    logoURI: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pull all the tags from all the tokens, reference or not
        all_tags = chain.from_iterable(
            list(token.tags) if token.tags else [] for token in self.tokens
        )
        # Obtain the set of all enumerated reference tags e.g. "1", "2", etc.
        token_ref_tags = {tag for tag in set(all_tags) if set(tag) < set("0123456789")}

        # Compare the enumerated reference tags from the tokens to the tag set in this class
        tokenlist_tags = set(iter(self.tags)) if self.tags else set()
        if token_ref_tags > tokenlist_tags:
            # We have an enumerated reference tag used by a token
            # missing from the our set of tags here
            raise ValueError(
                f"Missing reference tags in tokenlist: {token_ref_tags - tokenlist_tags}"
            )

    model_config = ConfigDict(frozen=False, extra="allow")

    @field_validator("logoURI")
    def validate_uri(cls, v: str | None) -> str | None:
        if v is None:
            return v

        if "://" not in v or not AnyUrl(v):
            raise ValueError(f"'{v}' is not a valid URI")

        return v

    def model_dump(self, *args, **kwargs) -> dict:
        data = super().model_dump(*args, **kwargs)

        if kwargs.get("mode", "").lower() == "json":
            # NOTE: This was the easiest way to make sure this property returns isoformat
            data["timestamp"] = self.timestamp.isoformat()

        return data

    @classmethod
    def create_empty(
        cls,
        name: str,
        logo_uri: str | None = None,
        keywords: list[str] | None = None,
    ) -> "TokenList":
        return cls(
            name=name,
            timestamp=cls._authoring_timestamp(),
            version=TokenListVersion(major=1, minor=0, patch=0),
            tokens=[],
            keywords=keywords or None,
            logoURI=logo_uri or None,
        )

    @classmethod
    def load(cls, path: str | Path) -> "TokenList":
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def save(self, path: str | Path) -> Path:
        tokenlist_path = Path(path)
        tokenlist_path.parent.mkdir(parents=True, exist_ok=True)
        tokenlist_path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        return tokenlist_path

    def add_token(self, token_info: TokenInfo) -> "TokenList":
        if any(
            token.chainId == token_info.chainId and token.address == token_info.address
            for token in self.tokens
        ):
            raise ValueError(
                f"Token at {token_info.address} on chain {token_info.chainId} already exists."
            )

        return self.model_validate(
            {
                **self.model_dump(),
                "tokens": [*self.tokens, token_info],
                "timestamp": self._authoring_timestamp(),
            }
        )

    def bump_version(self, part: Literal["major", "minor", "patch"] = "patch") -> "TokenList":
        new_version = self.version.model_copy(deep=True)

        match part:
            case "major":
                new_version.major += 1
                new_version.minor = 0
                new_version.patch = 0
            case "minor":
                new_version.minor += 1
                new_version.patch = 0
            case "patch":
                new_version.patch += 1

        return self.model_validate(
            {
                **self.model_dump(),
                "timestamp": self._authoring_timestamp(),
                "version": new_version,
            }
        )

    @staticmethod
    def _authoring_timestamp() -> datetime:
        return datetime.now(timezone.utc) - timedelta(seconds=1)
