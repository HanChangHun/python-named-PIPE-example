import os
from pathlib import Path
import select
import time

from utils.utils import make_pipe
from utils.pipe_lock import PIPELock


def receive_from_named_pipe(timeout):
    """Continuously monitor a named PIPE for incoming requests.

    Args:
        timeout (float): The time limit (in seconds) for waiting for incoming
            requests.
    """
    # Set timeout and create lock file path
    pipe_lock_path = "lock_practice/register_pipe_lock"
    pipe_lock = PIPELock(pipe_lock_path)

    # Create and open named PIPE
    pipe_path = Path("lock_practice/register_pipe")
    make_pipe(pipe_path)
    pipe = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    # Continuously monitor named PIPE for incoming requests
    start_time = time.time()
    while True:
        # Check if time limit exceeded
        if time.time() - start_time > timeout:
            break

        # Acquire lock and read incoming data from PIPE
        pipe_lock.acquire_lock()
        try:
            # Check for incoming requests through named PIPE
            rlist, _, _ = select.select([pipe], [], [], 1e-4)
            if rlist:
                pids = os.read(pipe, 1024).decode().strip()
                if pids:
                    print(f"Incoming request(s): {pids}")
                    # Process incoming data if not empty
                    for pid in pids.strip().split("\n"):
                        pid = int(pid)
                        print(f"Registered pid: {pid}")
        finally:
            # Release the lock for the named pipe
            pipe_lock.release_lock()

        # Pause execution briefly to avoid consuming too much resources
        time.sleep(1e-4)

    # Clean up named PIPE file
    pipe_path.unlink()


def main():
    """Run receive_from_named_pipe with a timeout of 10 seconds."""
    receive_from_named_pipe(timeout=10)


if __name__ == "__main__":
    main()
