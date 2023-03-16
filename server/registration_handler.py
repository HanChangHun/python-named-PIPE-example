import threading
from pathlib import Path
import time
from typing import Dict
from server.request_handler import RequestHandler

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

        self.registraion: Dict[int, RequestHandler] = dict()

        make_pipe(self.register_pipe_path)
        self.pipe_reader = PIPEReader(self.register_pipe_path)

    def start(self):
        self.register_th = threading.Thread(
            target=self.read_register_pipe_loop
        )
        self.register_th.start()

    def read_register_pipe_loop(self):
        while True:
            time.sleep(1e-9)
            self.read_register_pipe()

    def read_register_pipe(self):
        msgs = self.pipe_reader.read().strip()
        if msgs:
            for msg in msgs.split("\n"):
                msg_split = msg.split(" ")
                op = msg_split[0]
                pid = int(msg_split[1])
                self.handle_registration(op, pid)

    def handle_registration(self, op, pid):
        if op == "register":
            request_handler = RequestHandler(pid, logger=self.logger)
            self.registraion[pid] = request_handler
            request_handler.start()

            self.logger.log(f"[pid : {pid}] Client registration done.")

        elif op == "unregister":
            self.logger.log(f"[pid : {pid}] Get client unregistration")
            self.registraion[pid].stop()

            self.logger.log(f"[pid : {pid}] Client unregistration done")
