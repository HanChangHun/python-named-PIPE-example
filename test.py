from multiprocessing import Process
from pathlib import Path

from client.client import start_client
from server.server import start_server
from utils.multi_process_logger import MultiProcessLogger


def start_server_proc(register_pipe_path, logger) -> Process:
    proc = Process(target=start_server, args=(register_pipe_path, logger))
    proc.start()

    return proc


def start_client_proc(register_pipe_path, logger) -> Process:
    proc = Process(target=start_client, args=(register_pipe_path, logger))
    proc.start()

    return proc


def main() -> None:
    register_pipe_path = Path("register_pipe")
    logger = MultiProcessLogger(log_file=Path("logs/test.log"))

    server_proc = start_server_proc(register_pipe_path, logger)

    client_procs = []
    for _ in range(10):
        client_proc = start_client_proc(register_pipe_path, logger)
        client_procs.append(client_proc)

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

    logger.shutdown()


if __name__ == "__main__":
    main()
