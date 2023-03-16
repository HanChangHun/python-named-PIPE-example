import threading
import time
from pathlib import Path

from utils.multi_process_logger import MultiProcessLogger
from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter


class RequestHandler:
    """
    A class to handle client requests and send responses.
    """

    def __init__(self, pid, logger: MultiProcessLogger) -> None:
        """
        Initialize the RequestHandler object.
        """
        self.pid = pid
        self.logger = logger

        self.read_th = None
        self._stop = False

        self.read_pipe_path = Path(f"{pid}_to_server_pipe")
        self.write_pipe_path = Path(f"server_to_{pid}_pipe")

        self.read_pipe = PIPEReader(self.read_pipe_path)
        self.write_pipe = PIPEWriter(self.write_pipe_path)

    def __del__(self) -> None:
        """
        Destructor to stop the request handler.
        """
        self._stop = True

    def start(self):
        """
        Start the request handler's main loop.
        """
        self.read_th = threading.Thread(target=self.read_client_pipe_loop)
        self.read_th.start()

    def stop(self) -> None:
        """
        Stop the request handler.
        """
        self._stop = True

    def read_client_pipe_loop(self) -> None:
        """
        Continuously read client requests and handle them.

        If _stop is set to True, the read pipe and write pipe are deleted.
        """
        while not self._stop:
            time.sleep(1e-9)
            request = self.read_pipe.read(busy_wait=False)
            if request:
                self.logger.log(
                    f"[pid : {self.pid}] " f"Read from client: {request}"
                )
                self.handle(request)

        if self.write_pipe_path.exists():
            self.write_pipe_path.unlink()

        if self.read_pipe_path.exists():
            self.read_pipe_path.unlink()

        if self.write_pipe.pipe_lock.lock_file_path.exists():
            self.write_pipe.pipe_lock.lock_file_path.unlink()

        if self.read_pipe.pipe_lock.lock_file_path.exists():
            self.read_pipe.pipe_lock.lock_file_path.unlink()

    def handle(self, request_data: str) -> None:
        """
        Handle a client request.
        """
        data = self.parse_request(request_data)
        response = self.process_request(data)
        self.send_response(response)

    def parse_request(self, request_data: str) -> int:
        """
        Parse the request data.
        """
        return int(request_data)

    def process_request(self, data: int) -> int:
        """
        Process the request data.
        """
        return data * 2

    def send_response(self, response: int) -> None:
        """
        Send the response to the client.
        """
        msg = f"{response}"
        self.write_pipe.write(msg)
        self.logger.log(
            f"[pid : {self.pid} | server] Send response to client: {msg}"
        )
