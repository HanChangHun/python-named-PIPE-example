import os
from pathlib import Path

from utils.multi_process_logger import MultiProcessLogger
from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter
from utils.utils import make_pipe


class RequestSender:
    """
    A class to handle sending requests to the server and reading responses.
    """

    def __init__(self, pid: int, logger: MultiProcessLogger) -> None:
        """
        Initialize the RequestSender object.
        """
        self.pid = pid
        self.logger = logger

        self.write_pipe_path = Path(f"{self.pid}_to_server_pipe")
        self.read_pipe_path = Path(f"server_to_{self.pid}_pipe")

        make_pipe(self.write_pipe_path)
        make_pipe(self.read_pipe_path)

        self.write_pipe = PIPEWriter(self.write_pipe_path)
        self.read_pipe = PIPEReader(self.read_pipe_path)

    def __del__(self) -> None:
        """
        Cleanup the RequestSender object by unlinking the pipe files and lock files.
        """
        if self.write_pipe_path.exists():
            self.write_pipe_path.unlink()

        if self.read_pipe_path.exists():
            self.read_pipe_path.unlink()

        if self.write_pipe.pipe_lock.lock_file_path.exists():
            self.write_pipe.pipe_lock.lock_file_path.unlink()

        if self.read_pipe.pipe_lock.lock_file_path.exists():
            self.read_pipe.pipe_lock.lock_file_path.unlink()

    def request(self, data) -> int:
        """
        Send a request to the server and read the response.

        Returns:
            The response received from the server.
        """
        self.write_pipe.write(f"{data}")
        self.logger.log(f"[pid : {self.pid} | client] Send request: {data}")
        response = self.read_response(data)
        return response

    def read_response(self, org_data) -> int:
        """
        Read the response from the server and validate it.

        Returns:
            The validated response received from the server.

        Raises:
            Exception: If the response data is not correct.
        """
        response = self.read_pipe.read()
        while True:
            if response:
                self.logger.log(
                    f"[pid : {self.pid} | client] Received response: {response}"
                )
                if int(response) != org_data * 2:
                    raise Exception(
                        f"[pid : {self.pid} | client] "
                        f"Response data is not correct. "
                        f"Expected: {org_data * 2}, "
                        f"Received: {response}"
                    )
                break

        return int(response)
