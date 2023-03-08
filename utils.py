import os
import time


def make_pipe(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)


# Acquire the lock by creating the lock file with exclusive access
def acquire_lock(lock_file_path):
    while True:
        try:
            lock_file = os.open(
                lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
            return lock_file
        except OSError as e:
            # Failed to acquire lock, wait and try again
            time.sleep(1e-4)


# Release the lock by closing and deleting the lock file
def release_lock(lock_file, lock_file_path):
    os.close(lock_file)
    os.remove(lock_file_path)
