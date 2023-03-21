import time
from pathlib import Path
from typing import List
import zmq
from zmq import Poller, POLLIN


class PIPEReader:
    """
    A class to read data from a named pipe.
    """

    def __init__(self, pipe_path: Path):
        """
        Initialize the PIPEReader object.
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind(f"ipc://{pipe_path}")
        self.running = True

    def read(self, busy_wait=True) -> List[str]:
        """
        Read data from the pipe.

        Args:
            busy_wait (bool, optional): If True, keep trying to read the pipe until data is available.
                If False, return immediately if there is no data. Defaults to True.

        Returns:
            str: The data read from the pipe.
        """

        while self.running:
            try:
                if busy_wait:
                    message = self.socket.recv_string()
                else:
                    message = self.socket.recv_string(zmq.NOBLOCK)

                if message:
                    return message.strip().splitlines()

                if not busy_wait:
                    break

            except zmq.Again:
                pass

            except Exception as e:
                break

            time.sleep(1e-6)

        return []

    def close(self):
        """
        Stop the PIPEReader object.
        """
        self.running = False
        self.socket.close()
        self.context.term()
