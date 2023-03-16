import time
import threading
from pathlib import Path

from utils.multi_process_logger import MultiProcessLogger
from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class RegistrationHandler:
    def __init__(
        self,
        server,
        register_pipe_path: Path,
        logger: MultiProcessLogger,
    ):
        self.server = server
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self._stop = False
        self.registraion = dict()

        make_pipe(self.register_pipe_path)
        self.pipe_reader = PIPEReader(self.register_pipe_path)

    def start(self):
        register_th = threading.Thread(target=self.read_register_pipe_loop)
        register_th.start()

    def stop(self):
        self._stop = True
        del self.pipe_reader
        del self.registraion

    def read_register_pipe_loop(self):
        """
        Handles registration requests from clients via the register pipe.
        """
        while not self._stop:
            time.sleep(1e-4)
            self.read_register_pipe()

    def read_register_pipe(self):
        """
        Reads and handles a registration message from the register pipe.
        """
        msgs = self.pipe_reader.read().strip()
        if msgs:
            for msg in msgs.split("\n"):
                msg_split = msg.split(" ")
                op = msg_split[0]
                pid = int(msg_split[1])
                self.handle_registration(op, pid)

    def handle_registration(self, op, pid):
        if op == "register":
            handle = self.server.get_request_handler(pid)
            self.registraion[pid] = handle
            handle.start()

            self.logger.log(f"[pid : {pid}] Client registration done.")

        elif op == "unregister":
            self.registraion[pid].stop()
            del self.registraion[pid]

            self.logger.log(f"[pid : {pid}] Client unregistration done")
