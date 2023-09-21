from json import JSONDecodeError
from typing import Iterator, List, Optional

import requests

from tokenlists import config
from tokenlists.typing import ChainId, TokenInfo, TokenList, TokenSymbol


class TokenListManager:
    def __init__(self):
        # NOTE: Folder should always exist, even if empty
        self.cache_folder = config.DEFAULT_CACHE_PATH
        self.cache_folder.mkdir(exist_ok=True)

        # Load all the ones cached on disk
        self.installed_tokenlists = {}
        for path in self.cache_folder.glob("*.json"):
            tokenlist = TokenList.model_validate_json(path.read_text())
            self.installed_tokenlists[tokenlist.name] = tokenlist

        self.default_tokenlist = config.DEFAULT_TOKENLIST
        if not self.default_tokenlist:
            # Default might be cached on disk (does not override config)
            default_tokenlist_cachefile = self.cache_folder.joinpath(".default")

            if default_tokenlist_cachefile.exists():
                self.default_tokenlist = default_tokenlist_cachefile.read_text()

            elif len(self.installed_tokenlists) > 0:
                # Not cached on disk, use first installed list
                self.default_tokenlist = next(iter(self.installed_tokenlists))

    def install_tokenlist(self, uri: str) -> str:
        """
        Install the tokenlist at the given URI, return the name of the installed list
        (for reference purposes)
        """
        # This supports ENS lists
        if uri.endswith(".eth"):
            uri = config.UNISWAP_ENS_TOKENLISTS_HOST.format(uri)

        # Load and store the tokenlist
        response = requests.get(uri)
        response.raise_for_status()
        try:
            response_json = response.json()
        except JSONDecodeError as err:
            raise ValueError(f"Invalid response: {response.text}") from err

        tokenlist = TokenList.model_validate(response_json)
        self.installed_tokenlists[tokenlist.name] = tokenlist

        # Cache it on disk for later instances
        self.cache_folder.mkdir(exist_ok=True)
        token_list_file = self.cache_folder.joinpath(f"{tokenlist.name}.json")
        token_list_file.write_text(tokenlist.model_dump_json())

        return tokenlist.name

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
        self.cache_folder.mkdir(exist_ok=True)
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
        return filter(lambda t: t.chainId == chain_id, tokenlist.tokens)

    def get_token_info(
        self,
        symbol: TokenSymbol,
        token_listname: Optional[str] = None,  # Use default
        chain_id: ChainId = 1,  # Ethereum Mainnnet
        case_insensitive: bool = False,
    ) -> TokenInfo:
        tokenlist = self.get_tokenlist(token_listname)

        token_iter = filter(lambda t: t.chainId == chain_id, tokenlist.tokens)
        token_iter = (
            filter(lambda t: t.symbol == symbol, token_iter)
            if case_insensitive
            else filter(lambda t: t.symbol.lower() == symbol.lower(), token_iter)
        )

        matching_tokens = list(token_iter)
        if len(matching_tokens) == 0:
            raise ValueError(
                f"Token with symbol '{symbol}' does not exist"
                f" within '{tokenlist.name}' token list."
            )

        elif len(matching_tokens) > 1:
            raise ValueError(
                f"Multiple tokens with symbol '{symbol}'"
                f" found in '{tokenlist.name}' token list."
            )

        else:
            return matching_tokens[0]
