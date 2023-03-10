import fasteners
from pathlib import Path


class PIPELock:
    def __init__(self, pipe_path: Path, init: bool = False):
        """Create a new instance of the PIPELock class.

        Args:
            lock_file_path (Path): The path to the lock file.
            init (bool, optional): If set to True, initialize the lock file by
            removing it if it exists. Defaults to False.
        """
        self.lock_file_path = pipe_path.parent / f"{pipe_path.name}.lock"
        self.lock = fasteners.InterProcessLock(self.lock_file_path)

        self.init = init

        if init:
            self.init_lock()

    def init_lock(self) -> None:
        """Remove the lock file if it exists."""
        if self.lock_file_path.exists():
            self.lock_file_path.unlink()

    def acquire_lock(self) -> None:
        """Acquire the lock by creating the lock file with exclusive access."""
        self.lock.acquire()

    def release_lock(self) -> None:
        """Release the lock by closing and deleting the lock file.

        Raises:
            Exception: If the lock file is not open.
        """
        self.lock.release()
