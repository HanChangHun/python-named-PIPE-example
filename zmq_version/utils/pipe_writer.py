from pathlib import Path
import zmq


class PIPEWriter:
    """
    A class to write data to a named pipe.
    """

    def __init__(self, pipe_path: Path):
        """
        Initialize the PIPEWriter object.
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(f"ipc://{pipe_path}")
        self.running = True

    def write(self, message: str):
        """
        Write data to the pipe.
        """
        if self.running:
            self.socket.send_string(message)

    def close(self):
        """
        Stop the PIPEWriter object.
        """
        self.running = False
        self.socket.close()
        self.context.term()
