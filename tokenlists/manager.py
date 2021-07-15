import json
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import requests  # type: ignore
from dataclassy import dataclass

from tokenlists import config
from tokenlists.typing import ChainId, TokenInfo, TokenList, TokenSymbol


@dataclass
class TokenListManager:
    cache_folder: Path = config.DEFAULT_CACHE_PATH
    installed_tokenlists: Dict[str, TokenList] = {}
    default_tokenlist: Optional[str] = config.DEFAULT_TOKENLIST

    def __post_init__(self):
        # NOTE: Folder should always exist, even if empty
        self.cache_folder.mkdir(exist_ok=True)

        # Load all the ones cached on disk
        for path in self.cache_folder.glob("*.json"):
            with path.open() as fp:
                tokenlist = TokenList.from_dict(json.load(fp))
                self.installed_tokenlists[tokenlist.name] = tokenlist

        # Default might be cached on disk (does not override config)
        default_tokenlist_cachefile = self.cache_folder.joinpath(".default")
        if not self.default_tokenlist and default_tokenlist_cachefile.exists():
            self.default_tokenlist = default_tokenlist_cachefile.read_text()

    def install_tokenlist(self, uri: str):
        # This supports ENS lists
        if uri.endswith(".eth"):
            uri = config.UNISWAP_ENS_TOKENLISTS_HOST.format(uri)

        # Load and store the tokenlist
        tokenlist = TokenList.from_dict(requests.get(uri).json())
        self.installed_tokenlists[tokenlist.name] = tokenlist

        # Cache it on disk for later instances
        token_list_file = self.cache_folder.joinpath(f"{tokenlist.name}.json")
        with token_list_file.open("w") as fp:
            json.dump(tokenlist.to_dict(), fp)

    def remove_tokenlist(self, tokenlist_name: str) -> None:
        tokenlist = self.installed_tokenlists[tokenlist_name]

        if tokenlist.name == self.default_tokenlist:
            self.default_tokenlist = ""

        token_list_file = self.cache_folder.joinpath(f"{tokenlist.name}.json")
        token_list_file.unlink()

        del self.installed_tokenlists[tokenlist.name]

    def set_default_tokenlist(self, name: str) -> None:
        if name not in self.installed_tokenlists:
            raise ValueError(f"Unknown token list: {name}")

        self.default_tokenlist = name

        # Cache it on disk too
        self.cache_folder.joinpath(".default").write_text(name)

    def available_tokenlists(self) -> List[str]:
        return sorted(self.installed_tokenlists)

    def get_tokenlist(self, token_listname: Optional[str] = None) -> TokenList:
        if not token_listname:
            if not self.default_tokenlist:
                raise ValueError("Default token list has not been set.")

            token_listname = self.default_tokenlist

        if token_listname not in self.installed_tokenlists:
            raise ValueError(f"Unknown token list: {token_listname}")

        return self.installed_tokenlists[token_listname]

    def get_tokens(
        self,
        token_listname: Optional[str] = None,  # Use default
        chain_id: ChainId = 1,  # Ethereum Mainnnet
    ) -> Iterator[TokenInfo]:
        tokenlist = self.get_tokenlist(token_listname)
        return filter(lambda t: t.chainId == chain_id, iter(tokenlist))

    def get_token_info(
        self,
        symbol: TokenSymbol,
        token_listname: Optional[str] = None,  # Use default
        chain_id: ChainId = 1,  # Ethereum Mainnnet
        case_insensitive: bool = False,
    ) -> TokenInfo:
        tokenlist = self.get_tokenlist(token_listname)

        token_iter = filter(lambda t: t.chainId == chain_id, iter(tokenlist))
        token_iter = (
            filter(lambda t: t.symbol == symbol, token_iter)
            if case_insensitive
            else filter(lambda t: t.symbol.lower() == symbol.lower(), token_iter)
        )

        matching_tokens = list(token_iter)
        if len(matching_tokens) == 0:
            raise ValueError(
                f"Token with symbol '{symbol}' does not exist" f" within '{tokenlist}' token list."
            )

        elif len(matching_tokens) > 1:
            raise ValueError(
                f"Multiple tokens with symbol '{symbol}'" f" found in '{tokenlist}' token list."
            )

        else:
            return matching_tokens[0]
