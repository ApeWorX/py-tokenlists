from copy import deepcopy
from datetime import datetime as DateTime
from typing import Dict, Iterator, List, Optional, Union

import dataclassy as dc
from semantic_version import Version  # type: ignore

ChainId = int

TagId = str
URI = str

TokenAddress = str
TokenName = str
TokenDecimals = int
TokenSymbol = str


@dc.dataclass(frozen=True, slots=True)
class TokenInfo:
    chainId: ChainId
    address: TokenAddress
    name: TokenName
    decimals: TokenDecimals
    symbol: TokenSymbol
    logoURI: Optional[str] = None
    tags: Optional[List[TagId]] = None
    extensions: Optional[Dict[str, Union[str, int, bool]]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "TokenInfo":
        data = deepcopy(data)
        return cls(**data)  # type: ignore

    def to_dict(self) -> Dict:
        data = dc.asdict(self)
        if self.logoURI is None:
            del data["logoURI"]
        if self.tags is None:
            del data["tags"]
        if self.extensions is None:
            del data["extensions"]
        return data


class Timestamp(DateTime):
    def __init__(self, timestamp: str):
        super().fromisoformat(timestamp)


@dc.dataclass(frozen=True, slots=True)
class Tag:
    name: str
    description: str


# NOTE: Not frozen as we may need to dynamically modify this
@dc.dataclass(slots=True)
class TokenList:
    name: str
    timestamp: Timestamp
    version: Version
    tokens: List[TokenInfo]
    keywords: Optional[List[str]] = None
    tags: Optional[Dict[TagId, Tag]] = None
    logoURI: Optional[URI] = None

    def __iter__(self) -> Iterator[TokenInfo]:
        return iter(self.tokens)

    @classmethod
    def from_dict(cls, data: Dict) -> "TokenList":
        data = deepcopy(data)
        data["version"] = Version(**data["version"])
        data["tokens"] = [TokenInfo.from_dict(t) for t in data["tokens"]]
        return cls(**data)  # type: ignore

    def to_dict(self) -> Dict:
        data = dc.asdict(self)
        data["version"] = {
            "major": self.version.major,
            "minor": self.version.minor,
            "patch": self.version.patch,
        }
        data["tokens"] = [t.to_dict() for t in self.tokens]
        if self.keywords is None:
            del data["keywords"]
        if self.tags is None:
            del data["tags"]
        if self.logoURI is None or self.logoURI == "":
            del data["logoURI"]
        return data
