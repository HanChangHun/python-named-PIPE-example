from pathlib import Path
import threading
import time
from utils.multi_process_logger import MultiProcessLogger

from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter


class RequestHandler:
    def __init__(self, pid, logger: MultiProcessLogger):
        """Initializes the ClientHandler object."""
        self.pid = pid
        self.logger = logger

        self._stop = False

        self.read_pipe_path = Path(f"{pid}_to_server_pipe")
        self.write_pipe_path = Path(f"server_to_{pid}_pipe")

        self.read_pipe = PIPEReader(self.read_pipe_path)
        self.write_pipe = PIPEWriter(self.write_pipe_path)

    def start(self):
        read_th = threading.Thread(target=self.read_client_pipe_loop)
        read_th.start()

    def stop(self):
        self._stop = True

    def read_client_pipe_loop(self):
        while not self._stop:
            time.sleep(1e-4)
            request = self.read_pipe.read(busy_wait=False)
            if request:
                self.logger.log(
                    f"[pid : {self.pid}] " f"Read from client: {request}"
                )
                self.handle(request)

    def handle(self, request_data):
        """Handles the request from the client and sends the response back.

        Args:
            request_data (str): The request data received from the client.

        """
        data = self.parse_request(request_data)
        response = self.process_request(data)
        self.send_response(response)

    def parse_request(self, request_data: str) -> int:
        """Parses the request and converts it to an integer.

        Args:
            request (str): The request received from the client.

        Returns:
            int: The request value as an integer.
        """
        return int(request_data)

    def process_request(self, data: int) -> int:
        """Processes the request and generates the response.

        This method currently doubles the value of the request, but it can be
        modified to handle more complex logic in the future.

        Args:
            data (int): The request value as an integer.

        Returns:
            int: The response value as an integer.
        """
        return data * 2

    def send_response(self, response: int) -> None:
        """Sends the response to the client.

        Args:
            pid (int): The process ID of the client.
            response (int): The response value as an integer.
        """

        msg = f"{response}"
        self.write_pipe.write(msg)
        self.logger.log(
            f"[pid : {self.pid} | server] Send response to client: {msg}"
        )
