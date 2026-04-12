from collections.abc import Iterator
from json import JSONDecodeError
import warnings

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
        for path in sorted(self.cache_folder.glob("*.json")):
            tokenlist = TokenList.model_validate_json(path.read_text())
            self.installed_tokenlists[tokenlist.name] = tokenlist

        self.tokenlist_order = self._build_tokenlist_order()

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
        self.tokenlist_order = self._build_tokenlist_order()

        # Cache it on disk for later instances
        self.cache_folder.mkdir(exist_ok=True)
        token_list_file = self.cache_folder.joinpath(f"{tokenlist.name}.json")
        token_list_file.write_text(tokenlist.model_dump_json())

        return tokenlist.name

    def remove_tokenlist(self, tokenlist_name: str) -> None:
        tokenlist = self.installed_tokenlists[tokenlist_name]

        token_list_file = self.cache_folder.joinpath(f"{tokenlist.name}.json")
        token_list_file.unlink()

        del self.installed_tokenlists[tokenlist.name]
        self.tokenlist_order = self._build_tokenlist_order()

    def available_tokenlists(self) -> list[str]:
        return list(self.tokenlist_order)

    def get_tokenlist(self, token_listname: str) -> TokenList:
        if token_listname not in self.installed_tokenlists:
            raise ValueError(f"Unknown token list: {token_listname}")

        return self.installed_tokenlists[token_listname]

    def get_tokens(
        self,
        token_listname: str | None = None,
        chain_id: ChainId | None = None,
    ) -> Iterator[TokenInfo]:
        for tokenlist in self._iter_tokenlists(token_listname):
            for token in tokenlist.tokens:
                if chain_id is None or token.chainId == chain_id:
                    yield token

    def get_token_info(
        self,
        symbol: TokenSymbol,
        token_listname: str | None = None,
        chain_id: ChainId | None = None,
        case_insensitive: bool = False,
    ) -> TokenInfo:
        _, token_info = self.get_token_info_with_tokenlist(
            symbol,
            token_listname=token_listname,
            chain_id=chain_id,
            case_insensitive=case_insensitive,
        )
        return token_info

    def get_token_info_with_tokenlist(
        self,
        symbol: TokenSymbol,
        token_listname: str | None = None,
        chain_id: ChainId | None = None,
        case_insensitive: bool = False,
    ) -> tuple[str, TokenInfo]:
        for tokenlist in self._iter_tokenlists(token_listname):
            matching_tokens = self._get_matching_tokens(
                tokenlist, symbol, chain_id, case_insensitive
            )
            if len(matching_tokens) == 0:
                continue

            if len(matching_tokens) > 1:
                raise ValueError(
                    f"Multiple tokens with symbol '{symbol}' found in '{tokenlist.name}' token list."
                )

            return tokenlist.name, matching_tokens[0]

        if token_listname:
            raise ValueError(
                f"Token with symbol '{symbol}' does not exist within '{token_listname}' token list."
            )

        raise ValueError(f"Token with symbol '{symbol}' does not exist within installed token lists.")

    def _build_tokenlist_order(self) -> list[str]:
        installed_names = list(self.installed_tokenlists)
        configured_order = config.get_tokenlist_order()
        if configured_order is not None:
            ordered_names = []
            for name in configured_order:
                if name in self.installed_tokenlists and name not in ordered_names:
                    ordered_names.append(name)

            ordered_names.extend(name for name in installed_names if name not in ordered_names)
            return ordered_names

        return self._build_legacy_tokenlist_order(installed_names)

    def _build_legacy_tokenlist_order(self, installed_names: list[str]) -> list[str]:
        default_tokenlist_cachefile = self.cache_folder.joinpath(".default")
        if not default_tokenlist_cachefile.exists():
            return installed_names

        legacy_default = default_tokenlist_cachefile.read_text().strip()
        warnings.warn(
            (
                "The legacy `.default` tokenlist file is deprecated. "
                "Move your preferred ordering into `[tool.tokenlists].order` in `pyproject.toml`. "
                "Support for `.default` will be removed in an upcoming version."
            ),
            FutureWarning,
            stacklevel=2,
        )

        if legacy_default in self.installed_tokenlists:
            return [legacy_default, *(name for name in installed_names if name != legacy_default)]

        return installed_names

    def _iter_tokenlists(self, token_listname: str | None = None) -> Iterator[TokenList]:
        if token_listname:
            yield self.get_tokenlist(token_listname)
            return

        for name in self.tokenlist_order:
            yield self.installed_tokenlists[name]

    def _get_matching_tokens(
        self,
        tokenlist: TokenList,
        symbol: TokenSymbol,
        chain_id: ChainId | None,
        case_insensitive: bool,
    ) -> list[TokenInfo]:
        token_iter = (
            filter(lambda t: t.chainId == chain_id, tokenlist.tokens)
            if chain_id is not None
            else iter(tokenlist.tokens)
        )
        token_iter = (
            filter(lambda t: t.symbol.lower() == symbol.lower(), token_iter)
            if case_insensitive
            else filter(lambda t: t.symbol == symbol, token_iter)
        )
        return list(token_iter)
