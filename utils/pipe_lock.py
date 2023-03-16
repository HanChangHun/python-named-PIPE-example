import fasteners
from pathlib import Path


class PIPELock:
    """
    A class to manage read and write locks for inter-process communication.

    Attributes:
        lock_file_path (Path): The path to the lock file.
        lock (fasteners.InterProcessReaderWriterLock): The inter-process reader-writer lock.
        init (bool): Indicates if the lock needs to be initialized.
    """

    def __init__(self, pipe_path: Path, init: bool = False):
        """
        Initialize the PIPELock object.
        """
        self.lock_file_path = pipe_path.parent / f"{pipe_path.name}.lock"
        self.lock = fasteners.InterProcessReaderWriterLock(self.lock_file_path)

        self.init = init

        if init:
            self.init_lock()

    def init_lock(self) -> None:
        """
        Initialize the lock by removing the lock file if it exists.
        """
        if self.lock_file_path.exists():
            self.lock_file_path.unlink()

    def acquire_read_lock(self) -> None:
        self.lock.acquire_read_lock()

    def acquire_write_lock(self) -> None:
        self.lock.acquire_write_lock()

    def release_read_lock(self) -> None:
        self.lock.release_read_lock()

    def release_write_lock(self) -> None:
        self.lock.release_write_lock()
