import os
from pathlib import Path
import time


class PIPELock:
    def __init__(self, lock_file_path: Path, init=False):
        self.lock_file_path = lock_file_path
        self.lock_file = None

        if init:
            self.init_lock()

    def init_lock(self):
        if self.lock_file_path.exists():
            self.lock_file_path.unlink()

    # Acquire the lock by creating the lock file with exclusive access
    def acquire_lock(self):
        while True:
            try:
                self.lock_file = os.open(
                    self.lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
                )
                break
            except OSError as e:
                # Failed to acquire lock, wait and try again
                time.sleep(1e-9)

    # Release the lock by closing and deleting the lock file
    def release_lock(self):
        if self.lock_file is not None:
            os.close(self.lock_file)
            os.remove(self.lock_file_path)
            self.lock_file = None
        else:
            raise Exception("Lock file not open")
