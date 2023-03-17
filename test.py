import logging
from multiprocessing import Process, Queue
from pathlib import Path
from typing import List

from client.client import start_client
from server.server import start_server
from utils.multi_process_logger import LoggingProcess, MultiProcessLogger


def start_server_proc(register_pipe_path, logger, timeout) -> Process:
    proc = Process(
        target=start_server, args=(register_pipe_path, logger, timeout)
    )
    proc.start()

    return proc


def gen_client_proc(register_pipe_path, logger) -> Process:
    proc = Process(target=start_client, args=(register_pipe_path, logger))

    return proc


def main() -> None:
    register_pipe_path = Path("register_pipe")
    log_queue = Queue()
    logger = MultiProcessLogger(log_queue)

    logging_process = LoggingProcess(log_queue, log_file=Path("logs/test.log"))
    logging_process.start()

    timeout = 10
    server_proc = start_server_proc(register_pipe_path, logger, timeout)

    client_procs: List[Process] = []
    for _ in range(100):
        client_proc = gen_client_proc(register_pipe_path, logger)
        client_procs.append(client_proc)

    for client_proc in client_procs:
        client_proc.start()

    for client_proc in client_procs:
        client_proc.join()

    try:
        server_proc.join()
        if Path("register_pipe").exists():
            Path("register_pipe").unlink()
        if Path("register_pipe.lock").exists():
            Path("register_pipe.lock").unlink()

    except KeyboardInterrupt:
        if Path("register_pipe").exists():
            Path("register_pipe").unlink()
        if Path("register_pipe.lock").exists():
            Path("register_pipe.lock").unlink()

    log_queue.put("shutdown")
    logging_process.join()


if __name__ == "__main__":
    main()
