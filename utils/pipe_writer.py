from pathlib import Path


class PIPEWriter:
    """
    A class to write data to a named pipe.
    """

    def __init__(self, pipe_path: Path):
        """
        Initialize the PIPEWriter object.
        """
        self.pipe_path = pipe_path

    def write(self, message: str):
        """
        Write data to the pipe.
        """
        with open(self.pipe_path, mode="wb") as fifo:
            fifo.write((message + "\n").encode())
            fifo.flush()
