import os
from pathlib import Path

from utils.pipe_lock import PIPELock


class PIPEReader:
    def __init__(self, pipe_path: Path):
        """Initializes the PIPEReader object.

        Args:
            pipe_path (Path): The path to the pipe file to read from.
        """
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)
        self.pipe = os.open(self.pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    def __del__(self):
        del self.pipe_lock
        if self.pipe_path.exists():
            self.pipe_path.unlink()

    def read(self, busy_wait=True) -> str:
        """Reads the response from the pipe.

        Args:
            busy_wait (bool, optional): Whether or not to busy wait if there is no
            data in the pipe. Defaults to True.

        Returns:
            str: The response from the pipe as a string.
        """
        response = ""
        while True:
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
