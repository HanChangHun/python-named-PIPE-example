from multiprocessing import Process
from pathlib import Path
from typing import List

from client.client import start_client
from server.server import start_server


def start_server_proc(register_pipe_path, timeout) -> Process:
    proc = Process(
        target=start_server,
        args=(
            register_pipe_path,
            timeout,
        ),
    )
    proc.start()

    return proc


def main() -> None:
    register_pipe_path = Path("register_pipe")

    server_proc = start_server_proc(register_pipe_path, timeout=5)

    client_procs: List[Process] = []
    for _ in range(5):
        client_proc = Process(target=start_client, args=(register_pipe_path,))
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


if __name__ == "__main__":
    main()
