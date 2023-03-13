import os
from pathlib import Path
import select

from utils.pipe_lock import PIPELock


class PIPEReader:
    def __init__(self, pipe_path: Path):
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)
        self.pipe = os.open(self.pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    def read(self):
        """Reads the response from the pipe."""
        while True:
            self.pipe_lock.acquire_lock()
            try:
                rlist, _, _ = select.select([self.pipe], [], [], 1e-4)
                if rlist:
                    response = os.read(self.pipe, 1024).decode().strip()
                    if response:
                        break

            finally:
                self.pipe_lock.release_lock()

        return response
