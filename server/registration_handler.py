import threading
import time
from pathlib import Path
from typing import Dict

from server.request_handler import RequestHandler
from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class RegistrationHandler:
    """
    A class to handle client registration and unregistration.
    """

    def __init__(self, register_pipe_path: Path) -> None:
        """
        Initialize the RegistrationHandler object.
        """

        self.pipe_path = register_pipe_path

        self._stop = False

        self.register_th = None

        self.registration: Dict[int, RequestHandler] = dict()

        make_pipe(self.pipe_path)
        self.pipe_reader = PIPEReader(self.pipe_path)

    def start(self) -> None:
        """
        Start the registration handler's main loop.
        """
        self.register_th = threading.Thread(
            target=self.read_register_pipe_loop
        )
        self.register_th.start()

    def stop(self):
        """
        Stop the registration handler's main loop.
        """
        self._stop = True

    def read_register_pipe_loop(self) -> None:
        """
        Continuously read the register pipe and handle registration messages.
        """
        while not self._stop:
            time.sleep(1e-9)
            self.read_register_pipe()

    def read_register_pipe(self) -> None:
        """
        Read messages from the register pipe and handle them.
        """
        msgs = self.pipe_reader.read(busy_wait=False)
        if msgs:
            for msg in msgs:
                msg_split = msg.split(" ")
                if len(msg_split) != 2:
                    continue
                op = msg_split[0]
                pid = int(msg_split[1])
                self.handle_registration(op, pid)

    def handle_registration(self, op, pid) -> None:
        """
        Handle registration and unregistration messages.

        Args:
            op (str): The operation type ('register' or 'unregister').
            pid (int): The client process ID.
        """
        if op == "register":
            request_handler = RequestHandler(pid)
            self.registration[pid] = request_handler
            request_handler.start()

        elif op == "unregister":
            self.registration[pid].stop()
