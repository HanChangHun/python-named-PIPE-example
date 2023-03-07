import os


def make_pipe(path):
    if os.path.exists(path):
        os.remove(path)
    os.mkfifo(path)
