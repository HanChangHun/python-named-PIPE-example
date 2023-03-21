import threading
import time
import datetime
from pathlib import Path
from typing import List, Union

from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter


class RequestHandler:
    """
    A class to handle client requests and send responses.
    """

    def __init__(self, pid) -> None:
        """
        Initialize the RequestHandler object.
        """
        self.pid = pid

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
        self.read_pipe.close()
        self.write_pipe.close()

    def read_client_pipe_loop(self) -> None:
        """
        Continuously read client requests and handle them.

        If _stop is set to True, the read pipe and write pipe are deleted.
        """
        while not self._stop:
            requests = self.read_pipe.read(busy_wait=False)
            if requests:
                for request in requests:
                    # print(
                    #     f"[{datetime.datetime.now()}] get request: {request}"
                    # )
                    self.handle(request, cur_time=time.perf_counter_ns())
            time.sleep(1e-6)

        if self.write_pipe_path.exists():
            try:
                self.write_pipe_path.unlink()
            except FileNotFoundError:
                pass

        if self.read_pipe_path.exists():
            try:
                self.read_pipe_path.unlink()
            except FileNotFoundError:
                pass

    def handle(self, request: str, cur_time=None) -> None:
        """
        Handle a client request.
        """
        req_time, data = self.parse_request(request)
        if cur_time is not None and int(req_time) >= 0:
            print(
                f"[{datetime.datetime.now()}] ipc overhead: {(cur_time - int(req_time)) / 1000} us"
            )
        # print(f"[{datetime.datetime.now()}] parse request: {request}")
        response = self.process_request(data)
        # print(
        #     f"[{datetime.datetime.now()}] process request: {request} -> {response}"
        # )
        self.send_response(response)
        # print(f"[{datetime.datetime.now()}] send response: {response}")

    def parse_request(self, request_data: str) -> List[str]:
        """
        Parse the request data.
        """
        return request_data.split(" ")

    def process_request(self, data: str) -> int:
        """
        Process the request data.
        """
        if data == "init":
            return -1
        return int(data) * 2

    def send_response(self, response: int) -> None:
        """
        Send the response to the client.
        """
        msg = f"{response}"
        self.write_pipe.write(msg)
