from pathlib import Path

from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter


class ClientHandler:
    def __init__(self, pid):
        """Initializes the ClientHandler object."""
        self.pid = pid
        self.read_pipe_path = Path(f"{pid}_to_server_pipe")
        self.write_pipe_path = Path(f"server_to_{pid}_pipe")

        self.read_pipe = PIPEReader(self.read_pipe_path)
        self.write_pipe = PIPEWriter(self.write_pipe_path)

    def __del__(self):
        """Destructor of ClientHandler object.

        Removes the read pipe, write pipe, and lock files if they exist.
        """
        if self.write_pipe_path.exists():
            self.write_pipe_path.unlink()

        if self.read_pipe_path.exists():
            self.read_pipe_path.unlink()

        if self.write_pipe.pipe_lock.lock_file_path.exists():
            self.write_pipe.pipe_lock.lock_file_path.unlink()

        if self.read_pipe.pipe_lock.lock_file_path.exists():
            self.read_pipe.pipe_lock.lock_file_path.unlink()

    def read(self):
        """Reads from the read pipe.

        Returns:
            str: The data read from the pipe.

        """
        return self.read_pipe.read(busy_wait=False)

    def write(self, msg):
        """Writes to the write pipe.

        Args:
            msg (str): The message to be written to the pipe.

        """
        self.write_pipe.write(msg)

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
        self.write(msg)
        print(f"[pid: {self.pid} | server] Send response to client: {msg}")
