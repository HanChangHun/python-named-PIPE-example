import os
import time
from pathlib import Path

from utils.pipe_lock import PIPELock


class PIPEReader:
    def __init__(self, pipe_path: Path):
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)
        self.pipe = os.open(self.pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    def __del__(self):
        os.close(self.pipe)

    def read(self, busy_wait=True) -> str:
        response = ""
        while True:
            time.sleep(1e-9)
            self.pipe_lock.acquire_read_lock()
            try:
                response = b""
                while True:
                    chunk = os.read(self.pipe, 1024)
                    if not chunk:
                        break
                    response += chunk

                if response:
                    response = response.decode().strip()
                    break

                if not busy_wait:
                    break

            finally:
                self.pipe_lock.release_read_lock()

        return response
