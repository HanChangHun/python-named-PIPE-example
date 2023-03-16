import subprocess
import threading
from multiprocessing import Process
from pathlib import Path

from client.client import start_client
from server.server import start_server
from utils.multi_process_logger import MultiProcessLogger


def start_server_proc(logger) -> Process:
    """Start a separate process to receive data from a named pipe."""
    proc = Process(target=start_server, args=(logger,))
    proc.start()
    return proc


def start_server_th(logger) -> threading.Thread:
    """Start a separate process to send data to a named pipe."""
    th = threading.Thread(target=start_server, args=(logger,))
    th.start()
    return th


def start_client_proc(logger) -> None:
    """Start a separate process to send data to a named pipe."""
    proc = Process(target=start_client, args=(logger,))
    proc.start()


def main() -> None:
    """Start two processes, one to receive data and two to send data."""
    logger = MultiProcessLogger(
        flush_interval=1e-4, log_file=Path("logs/test.log")
    )

    server_proc = start_server_proc(logger)
    # server_th = start_server_th(logger)
    for _ in range(1):
        start_client_proc(logger)

    try:
        server_proc.join()
        # server_th.join()
    except KeyboardInterrupt:
        pass

    logger.shutdown()


if __name__ == "__main__":
    main()
