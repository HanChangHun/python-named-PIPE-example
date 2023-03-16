import os
import time
from pathlib import Path

from utils.pipe_lock import PIPELock


class PIPEWriter:
    """
    A class to write data to a named pipe.
    """

    def __init__(self, pipe_path: Path):
        """
        Initialize the PIPEWriter object.
        """
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)
        self.pipe = None

    def write(self, message: str):
        """
        Write data to the pipe.

        Raises:
            Exception: If an error occurs while writing to the pipe.
        """
        self.pipe_lock.acquire_write_lock()
        while True:
            try:
                self.pipe = os.open(
                    self.pipe_path, os.O_WRONLY | os.O_NONBLOCK
                )
                break

            except Exception as e:
                # TODO: Find a better way to handle this.
                # It raise error at first client side request.
                # Why there is time between make pipe and open pipe?
                print(e)
                time.sleep(1e-9)

        try:
            os.write(self.pipe, message.encode())

        except Exception as e:
            print(f"Error writing to pipe: {str(message)}")
            raise e

        finally:
            os.close(self.pipe)
            self.pipe_lock.release_write_lock()
