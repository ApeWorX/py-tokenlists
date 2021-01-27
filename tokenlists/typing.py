from typing import Dict, Iterator, List, NewType, Optional, Union

from datetime import datetime as DateTime
from copy import deepcopy
from eth_typing import ChecksumAddress
from semantic_version import Version  # type: ignore

import dataclasses as dc

ChainId = NewType("ChainId", int)

TagId = NewType("TagId", str)
URI = NewType("URI", str)

TokenAddress = ChecksumAddress
TokenName = NewType("TokenName", str)
TokenDecimals = NewType("TokenDecimals", int)
TokenSymbol = NewType("TokenSymbol", str)


@dc.dataclass(frozen=True)
class TokenInfo:
    chainId: ChainId
    address: TokenAddress
    name: TokenName
    decimals: TokenDecimals
    symbol: TokenSymbol
    logoURI: Optional[URI] = URI("")
    tags: Optional[List[TagId]] = None
    extensions: Dict[str, Union[str, int, bool]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "TokenInfo":
        data = deepcopy(data)
        return TokenInfo(**data)

    def to_dict(self) -> Dict:
        data = dc.asdict(self)
        if self.logoURI == "":
            del data["logoURI"]
        if self.tags is None:
            del data["tags"]
        if self.extensions is None:
            del data["extensions"]
        return data


class Timestamp(DateTime):
    def __init__(self, timestamp: str):
        super().fromisoformat(timestamp)


@dc.dataclass(frozen=True)
class ListVersion(Version):
    major: int
    minor: int
    patch: int


@dc.dataclass(frozen=True)
class Tag:
    name: str
    description: str


@dc.dataclass
class TokenList:
    name: str
    timestamp: Timestamp
    version: ListVersion
    tokens: List[TokenInfo]
    keywords: Optional[List[str]] = None
    tags: Optional[Dict[TagId, Tag]] = None
    logoURI: Optional[URI] = URI("")

    def __iter__(self) -> Iterator[TokenInfo]:
        for token_info in self.tokens:
            yield token_info

    @classmethod
    def from_dict(cls, data: Dict) -> "TokenList":
        data = deepcopy(data)
        data["version"] = ListVersion(**data["version"])
        data["tokens"] = [TokenInfo.from_dict(t) for t in data["tokens"]]
        return TokenList(**data)

    def to_dict(self) -> Dict:
        data = dc.asdict(self)
        data["tokens"] = [t.to_dict() for t in self.tokens]
        if self.keywords is None:
            del data["keywords"]
        if self.tags is None:
            del data["tags"]
        if self.logoURI == "":
            del data["logoURI"]
        return data
