from multiprocessing import Process
import subprocess

from server import start_server
from client import start_client


def start_server_proc() -> Process:
    """Start a separate process to receive data from a named pipe."""
    proc = Process(target=start_server)
    proc.start()
    return proc


def start_client_proc() -> None:
    """Start a separate process to send data to a named pipe."""
    proc = Process(target=start_client)
    proc.start()


def main() -> None:
    """Start two processes, one to receive data and two to send data."""
    server_proc = start_server_proc()
    for _ in range(100):
        start_client_proc()

    try:
        server_proc.join()
    except KeyboardInterrupt:
        subprocess.run(["rm *_pipe *.lock"], shell=True)


if __name__ == "__main__":
    main()
