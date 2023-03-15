import os
from pathlib import Path
from utils.pipe_lock import PIPELock

from utils.utils import make_pipe


def read(pipe, pipe_lock, busy_wait=True) -> str:
    """Reads the response from the pipe.

    Args:
        busy_wait (bool, optional): Whether or not to busy wait if there is no
        data in the pipe. Defaults to True.

    Returns:
        str: The response from the pipe as a string.
    """
    response = ""
    while True:
        pipe_lock.acquire_read_lock()
        try:
            response = b""
            while True:
                chunk = os.read(pipe, 1024)
                if not chunk:
                    break
                response += chunk
                print(f"chunk: {chunk.decode()}")

            if response:
                response = response.decode().strip()
                break

            if not busy_wait:
                break

        finally:
            pipe_lock.release_read_lock()

    return response


def main():
    pipe_path = Path("pipe_read_practice/pipe")
    make_pipe(pipe_path)

    pipe_lock = PIPELock(pipe_path)

    pipe = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    while True:
        response = read(pipe, pipe_lock)
        print(f"response: {response}")


if __name__ == "__main__":
    main()
