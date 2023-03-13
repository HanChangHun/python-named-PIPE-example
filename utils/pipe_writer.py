import os
from pathlib import Path

from utils.pipe_lock import PIPELock


class PIPEWriter:
    def __init__(self, pipe_path: Path):
        self.pipe_path = pipe_path
        self.pipe_lock = PIPELock(pipe_path)

    def write(self, message: str):
        self.pipe_lock.acquire_lock()
        self.pipe = os.open(self.pipe_path, os.O_WRONLY)
        try:
            os.write(self.pipe, message.encode())

        except Exception as e:
            print(f"Error writing to pipe: {str(message)}")
            raise e

        finally:
            os.close(self.pipe)
            self.pipe_lock.release_lock()
