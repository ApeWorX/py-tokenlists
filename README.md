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

## License

This project is licensed under the [MIT license](LICENSE).
