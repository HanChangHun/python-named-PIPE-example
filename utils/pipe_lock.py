import fasteners
from pathlib import Path


class PIPELock:
    def __init__(self, pipe_path: Path, init: bool = False):
        self.lock_file_path = pipe_path.parent / f"{pipe_path.name}.lock"
        self.lock = fasteners.InterProcessReaderWriterLock(self.lock_file_path)

        self.init = init

        if init:
            self.init_lock()

    def init_lock(self) -> None:
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
