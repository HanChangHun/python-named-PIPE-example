import fcntl
import os
import time
from pathlib import Path


class PIPEReader:
    """
    A class to read data from a named pipe.
    """

    def __init__(self, pipe_path: Path):
        """
        Initialize the PIPEReader object.
        """
        self.pipe_path = pipe_path
        self.pipe_fd = os.open(self.pipe_path, os.O_RDONLY | os.O_NONBLOCK)
        flags = fcntl.fcntl(self.pipe_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.pipe_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

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

            response = ""
            try:
                response = os.read(self.pipe_fd, 512).decode().strip()
                if response:
                    break

                if not busy_wait:
                    break

            except Exception as e:
                pass

        return response
