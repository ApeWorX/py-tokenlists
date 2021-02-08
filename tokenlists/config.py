from pathlib import Path
from typing import Optional

DATA_FOLDER = Path.home().joinpath(".tokenlists")
DEFAULT_TOKEN_LIST: Optional[str] = None

UNISWAP_ENS_TOKENLISTS_HOST = "https://wispy-bird-88a7.uniswap.workers.dev/?url=http://{}.link"
