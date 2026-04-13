# py-tokenlists

[Uniswap Token Lists](https://github.com/Uniswap/token-lists) implementation in Python.

## Dependencies

- [python3](https://www.python.org/downloads/release/python-368/) version 3.8 or greater, python3-dev

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install tokenlists
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/py-tokenlists.git
cd py-tokenlists
python3 setup.py install
```

## Quick Usage

```python
>>> from tokenlists import TokenListManager
>>> tlm = TokenListManager()

>>> tlm.available_tokenlists()
[]

>>> tlm.install_tokenlist("tokens.1inch.eth")
>>> tlm.available_tokenlists()
['1inch']
```

You can also author and test your own token list locally before publishing it:

```bash
tokenlists new ./tokenlist.json --name "My Token List" --keyword defi --keyword dex
tokenlists add ./tokenlist.json --chain-id 1 --address 0x0000000000000000000000000000000000000001 --name "Token" --symbol TKN --decimals 18 --tag stablecoin
tokenlists install ./tokenlist.json
```

If you omit required options from `tokenlists new` or `tokenlists add`, the CLI will prompt for the missing values. When a token is added to a list, the list timestamp is refreshed and the semantic version is bumped from `major.minor.patch` to the next minor version, following the token list update rules for additive changes.

Publishing is simply serving the generated JSON somewhere reachable by your users. Once hosted, install and verify it with `tokenlists install <url>`.

Token lookup order is controlled locally through `pyproject.toml`:

```toml
[tool.tokenlists]
order = ["My Preferred List", "Fallback List"]
```

HTTP downloads use `httpx` and honor the standard environment variables that HTTPX documents for restricted networks and custom trust stores, including `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, `SSL_CERT_FILE`, and `SSL_CERT_DIR`.

## License

This project is licensed under the [MIT license](LICENSE).
