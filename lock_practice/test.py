from multiprocessing import Process

from lock_practice.receiver import receive_from_named_pipe
from lock_practice.sender import request_to_named_pipe


def start_receiver() -> None:
    """Start a separate process to receive data from a named pipe."""
    # Create a new process to run the receive_from_named_pipe function with a timeout of 10 seconds.
    proc = Process(target=receive_from_named_pipe, args=(10,))
    proc.start()


def start_sender() -> None:
    """Start a separate process to send data to a named pipe."""
    proc = Process(target=request_to_named_pipe, args=(None,))
    proc.start()


def main():
    """Start two processes, one to receive data and two to send data."""
    start_receiver()
    start_sender()
    start_sender()


if __name__ == "__main__":
    main()
