import os
import select
import time

from utils import acquire_lock, release_lock


def write_to_named_pipe(data):
    """
    Write data to the named pipe while acquiring a lock

    Args:
        data: The data to write to the named pipe
    """

    # Define the path to the lock file
    pipe_lock_path = "lock_test/lock"

    # Define the path to the named pipe and open it for writing
    pipe_path = f"lock_test/register_pipe"
    pipe = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)

    # Acquire the lock for the named pipe
    pipe_lock = acquire_lock(pipe_lock_path)

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
        release_lock(pipe_lock, pipe_lock_path)


if __name__ == "__main__":
    # Call the write_to_named_pipe function with the current process ID
    write_to_named_pipe(f"{os.getpid()}\n")
