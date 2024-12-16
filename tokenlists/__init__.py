def __getattr__(name: str):
    if name == "TokenInfo":
        from tokenlists.typing import TokenInfo

        return TokenInfo

    elif name == "TokenList":
        from tokenlists.typing import TokenList

        return TokenList

    elif name == "TokenListManager":
        from tokenlists.manager import TokenListManager

        return TokenListManager

    else:
        raise AttributeError(name)


__all__ = [
    "TokenInfo",
    "TokenList",
    "TokenListManager",
]
