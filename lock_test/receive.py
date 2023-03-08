import os
from pathlib import Path
import select
import time

from utils import acquire_lock, make_pipe, release_lock


def main():
    # Set timeout and create lock file path
    timeout = 10
    lock_file_path = "lock_test/lock"

    # Create and open named PIPE
    pipe_path = Path("lock_test/register_pipe")
    make_pipe(pipe_path)
    pipe = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)

    # Continuously monitor named PIPE for incoming requests
    start_time = time.time()
    while True:
        # Check if time limit exceeded
        if time.time() - start_time > timeout:
            break

        # Acquire lock and read incoming data from PIPE
        lock_file = acquire_lock(lock_file_path)
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
            release_lock(lock_file, lock_file_path)

        # Pause execution briefly to avoid consuming too much resources
        time.sleep(1e-4)

    # Clean up named PIPE file
    pipe_path.unlink()


if __name__ == "__main__":
    main()
