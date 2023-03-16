import os
import time
from pathlib import Path

from utils.pipe_lock import PIPELock


class PIPEReader:
    """
    A class to read data from a named pipe.
    """

    def __init__(self, pipe_path: Path):
        """
        Initialize the PIPEReader object.
        """
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)
        self.pipe = os.open(self.pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    def __del__(self):
        """
        Close the pipe when the object is deleted.
        """
        os.close(self.pipe)

    def read(self, busy_wait=True) -> str:
        """
        Read data from the pipe.

        Args:
            busy_wait (bool, optional): If True, keep trying to read the pipe until data is available.
                If False, return immediately if there is no data. Defaults to True.

        Returns:
            str: The data read from the pipe.
        """
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
