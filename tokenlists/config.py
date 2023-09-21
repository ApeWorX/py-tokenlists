from pathlib import Path
from typing import Optional

DEFAULT_CACHE_PATH = Path.home().joinpath(".tokenlists")
DEFAULT_TOKENLIST: Optional[str] = None

UNISWAP_ENS_TOKENLISTS_HOST = "https://wispy-bird-88a7.uniswap.workers.dev/?url=http://{}.link"
