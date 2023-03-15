import os
from pathlib import Path
import time

from utils.pipe_lock import PIPELock


def write(pipe_path, pipe_lock, message: str):
    """Writes a message to the pipe.

    Acquires a lock on the pipe and writes the message to the pipe.

    Args:
        message (str): The message to write to the pipe.
    """
    pipe_lock.acquire_write_lock()

    while True:
        try:
            pipe = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)
            break
        except Exception as e:
            time.sleep(1e-1)

    try:
        os.write(pipe, message.encode())

    except Exception as e:
        print(f"Error writing to pipe: {str(message)}")
        raise e

    finally:
        os.close(pipe)
        pipe_lock.release_write_lock()


def main():
    pipe_path = Path("pipe_read_practice/pipe")
    pipe_lock = PIPELock(pipe_path)
    # pipe = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)

    # write(pipe, pipe_lock, "Hello, world!5")
    write(pipe_path, pipe_lock, "Hello, world!6")


if __name__ == "__main__":
    main()
