import os
from pathlib import Path
import time

from utils.pipe_lock import PIPELock


class PIPEWriter:
    def __init__(self, pipe_path: Path):
        """Initialize the PIPEWriter object.

        Args:
            pipe_path (Path): The path to the pipe to write to.
        """
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)

    def __del__(self):
        del self.pipe_lock
        if self.pipe_path.exists():
            self.pipe_path.unlink()

    def write(self, message: str):
        """Writes a message to the pipe.

        Acquires a lock on the pipe and writes the message to the pipe.

        Args:
            message (str): The message to write to the pipe.
        """
        self.pipe_lock.acquire_write_lock()

        while True:
            try:
                self.pipe = os.open(
                    self.pipe_path, os.O_WRONLY | os.O_NONBLOCK
                )
                break
            except Exception as e:
                time.sleep(1e-1)

        try:
            os.write(self.pipe, message.encode())

        except Exception as e:
            print(f"Error writing to pipe: {str(message)}")
            raise e

        finally:
            os.close(self.pipe)
            self.pipe_lock.release_write_lock()
