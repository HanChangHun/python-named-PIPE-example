import os
from pathlib import Path


def make_pipe(path: Path) -> None:
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)
