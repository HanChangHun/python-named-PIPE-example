from multiprocessing import Process

from server import start_server
from client import start_client


def start_server_proc() -> None:
    """Start a separate process to receive data from a named pipe."""
    proc = Process(target=start_server)
    proc.start()


def start_client_proc() -> None:
    """Start a separate process to send data to a named pipe."""
    proc = Process(target=start_client)
    proc.start()


def main() -> None:
    """Start two processes, one to receive data and two to send data."""
    # start_server_proc()
    for _ in range(5):
        start_client_proc()


if __name__ == "__main__":
    main()
