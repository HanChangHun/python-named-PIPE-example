import os
from pathlib import Path
import random
import select
import time


class Client:
    def __init__(self):
        self.register_pipe_path = Path("register_pipe")
        self.pid = os.getpid()
        self.send_pipe_path = Path(f"{self.pid}_to_server_pipe")
        self.receive_pipe_path = Path(f"server_to_{self.pid}_pipe")

    def __del__(self):
        if self.send_pipe_path.exists():
            self.send_pipe_path.unlink()

        if self.receive_pipe_path.exists():
            self.receive_pipe_path.unlink()

    def register(self):
        self.register_pipe = os.open(self.register_pipe_path, os.O_WRONLY)
        while True:
            time.sleep(1e-4)
            _, wlist, _ = select.select([], [self.register_pipe], [], 1e-4)
            if wlist:
                msg = f"{self.pid}".encode()
                os.write(self.register_pipe, msg)
                os.close(self.register_pipe)
                print(f"Registered")
                break

    def request(self):
        for _ in range(10):
            time.sleep(1)
            self.send_pipe = os.open(self.send_pipe_path, os.O_WRONLY)
            self.receive_pipe = os.open(
                self.receive_pipe_path, os.O_RDONLY | os.O_NONBLOCK
            ) # it should be non-blocking!
            data = random.randint(0, 100)
            msg = f"{data}".encode()

            while True:
                time.sleep(1e-4)
                _, wlist, _ = select.select([], [self.send_pipe], [], 1e-4)
                if wlist:
                    os.write(self.send_pipe, msg)
                    print(f"Send request: {msg.decode()}")
                    os.close(self.send_pipe)
                    break

            while True:
                time.sleep(1e-4)
                rlist, _, _ = select.select([self.receive_pipe], [], [], 1e-4)
                if rlist:
                    response = os.read(self.receive_pipe, 1024).decode()
                    print(f"Received response: {response}")
                    break


def main():
    client = Client()
    client.register()
    client.request()


if __name__ == "__main__":
    main()
