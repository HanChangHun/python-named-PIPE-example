import os
from pathlib import Path


def make_pipe(path: Path) -> None:
    """Create a named pipe at the specified path.

    Args:
        path (Path): The path where the named pipe will be created.

    Returns:
        None: This function returns nothing.

    Raises:
        OSError: If the named pipe already exists and cannot be removed.
    """
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)
