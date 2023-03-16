from pathlib import Path
from utils.multi_process_logger import MultiProcessLogger

from utils.utils import make_pipe
from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter


class RequestSender:
    def __init__(self, pid: int, logger: MultiProcessLogger):
        self.pid = pid
        self.logger = logger

        self.write_pipe_path = Path(f"{self.pid}_to_server_pipe")
        self.read_pipe_path = Path(f"server_to_{self.pid}_pipe")

        make_pipe(self.write_pipe_path)
        make_pipe(self.read_pipe_path)

        self.write_pipe = PIPEWriter(self.write_pipe_path)
        self.read_pipe = PIPEReader(self.read_pipe_path)

    def __del__(self):
        if self.write_pipe_path.exists():
            self.write_pipe_path.unlink()

        if self.read_pipe_path.exists():
            self.read_pipe_path.unlink()

        if self.write_pipe.pipe_lock.lock_file_path.exists():
            self.write_pipe.pipe_lock.lock_file_path.unlink()

        if self.read_pipe.pipe_lock.lock_file_path.exists():
            self.read_pipe.pipe_lock.lock_file_path.unlink()

    def request(self, data) -> None:
        self.write_pipe.write(f"{data}")
        self.logger.log(f"[pid : {self.pid} | client] Send request: {data}")
        response = self.read_response(data)
        return response

    def read_response(self, org_data) -> None:
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

        return response
