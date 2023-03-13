from multiprocessing import Process
from pathlib import Path
import subprocess
import threading
from multi_process_logger import MultiProcessLogger

from server import start_server
from client import start_client


def start_server_proc(logger) -> Process:
    """Start a separate process to receive data from a named pipe."""
    proc = Process(target=start_server, args=(logger,))
    proc.start()
    return proc


def start_client_proc(logger) -> None:
    """Start a separate process to send data to a named pipe."""
    proc = Process(target=start_client, args=(logger,))
    proc.start()


def main() -> None:
    """Start two processes, one to receive data and two to send data."""
    logger = MultiProcessLogger(flush_interval=1e-4, log_file=Path("test.log"))

    server_proc = start_server_proc(logger)
    for _ in range(5):
        start_client_proc(logger)

    try:
        server_proc.join()
    except KeyboardInterrupt:
        subprocess.run(["rm *_pipe *.lock"], shell=True)

    logger.shutdown()


if __name__ == "__main__":
    main()
