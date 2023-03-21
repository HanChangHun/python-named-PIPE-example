import os
from pathlib import Path


def make_pipe(path: Path) -> None:
    """
    Create a named pipe (FIFO) at the specified path.

    If a file already exists at the path, it is removed and a new pipe is created.

    Args:
        path (Path): The path to create the named pipe.
    """
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)
