from multiprocessing import Process

from lock_practice.receiver import receive_from_named_pipe
from lock_practice.sender import request_to_named_pipe


def start_receiver():
    proc = Process(target=receive_from_named_pipe, args=(10,))
    proc.start()


def start_sender():
    proc = Process(target=request_to_named_pipe, args=(None,))
    proc.start()


def main():
    start_receiver()
    start_sender()
    start_sender()


if __name__ == "__main__":
    main()
