import os
import select
import threading
from pathlib import Path
import time

from utils import make_pipe


class Server:
    def __init__(self):
        self.regiter_pipe_path = Path("register_pipe")
        self.registered_pids = []

        self.init_register_pipe()

    def __del__(self):
        self.regiter_pipe_path.unlink()

    def init_register_pipe(self):
        make_pipe(self.regiter_pipe_path)
        self.regiter_pipe = os.open(self.regiter_pipe_path, os.O_RDONLY)

    def start(self):
        register_th = threading.Thread(target=self.start_register_pipe)
        register_th.start()

    def start_register_pipe(self):
        while True:
            time.sleep(1e-4)
            rlist, _, _ = select.select([self.regiter_pipe], [], [], 1e-4)
            if rlist:
                pid = os.read(self.regiter_pipe, 1024).decode()
                if pid and pid.strip():
                    pid = int(pid)
                    self.registered_pids.append(pid)
                    print(f"Registered pid: {pid}")
                    self.make_read_pipe(pid)
                    self.start_read_client(pid)

    def make_read_pipe(self, pid):
        receive_pipe_path = Path(f"{pid}_to_server_pipe")
        send_pipe_path = Path(f"server_to_{pid}_pipe")
        make_pipe(send_pipe_path)
        make_pipe(receive_pipe_path)

    def start_read_client(self, pid):
        def read_client():
            receive_pipe_path = Path(f"{pid}_to_server_pipe")
            receive_pipe = os.open(receive_pipe_path, os.O_RDONLY)
            while True:
                rlist, _, _ = select.select([receive_pipe], [], [])
                if rlist:
                    request = os.read(receive_pipe, 1024).decode()
                    if request and request.strip():
                        print(f"Read from client {pid}: {request}")
                        self.handle_request(pid, request)

        read_th = threading.Thread(target=read_client)
        read_th.start()

    def handle_request(self, pid, request):
        send_pipe_path = Path(f"server_to_{pid}_pipe")
        send_pipe = os.open(send_pipe_path, os.O_WRONLY)
        data = int(request)
        msg = f"{data * 2}".encode()

        while True:
            time.sleep(1e-4)
            _, wlist, _ = select.select([], [send_pipe], [], 1e-4)
            if wlist:
                os.write(send_pipe, msg)
                print(f"Send response to client {pid}: {msg.decode()}")
                os.close(send_pipe)
                break
        return data * 2


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
