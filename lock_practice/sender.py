import os
from pathlib import Path
import select
import time
from utils.pipe_lock import PIPELock


def request_to_named_pipe(data: str = None):
    """Write data to a named PIPE while acquiring a lock.

    Args:
        data (str, optional): The data to write to the named PIPE. If None,
            use the current process ID. Defaults to None.
    """

    if data is None:
        data = f"{os.getpid()}\n"

    # Define the path to the lock file

    # Define the path to the named pipe and open it for writing
    pipe_path = Path("lock_practice/register_pipe")
    pipe = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)

    # Get the lock file
    pipe_lock = PIPELock(pipe_path)

    # Acquire the lock for the named pipe
    pipe_lock.acquire_lock()
    try:
        # Check if the pipe is ready for writing using select
        _, wlist, _ = select.select([], [pipe], [], 1e-4)
        if wlist:
            # Write the data to the named pipe and close the pipe
            os.write(pipe, str(data).encode())
            os.close(pipe)
            print("writing done: ", data)

        # Sleep for test
        time.sleep(3)
    finally:
        # Release the lock for the named pipe
        pipe_lock.release_lock()


if __name__ == "__main__":
    # Call the write_to_named_pipe function with the current process ID
    request_to_named_pipe(f"{os.getpid()}\n")
