import logging
import multiprocessing
from pathlib import Path
import time
import sys
import inspect


class MultiProcessLogger:
    def __init__(
        self,
        log_level=logging.INFO,
        flush_interval=1e-4,
        log_file: Path = None,
    ):
        self.log_level = log_level
        self.flush_interval = flush_interval
        self.log_file = log_file

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)

        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)04d] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(self.log_level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        if self.log_file:
            if self.log_file.exists():
                self.log_file.unlink()
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.log_queue = multiprocessing.Queue()
        self.log_process = multiprocessing.Process(target=self._flush_logs)
        self.log_process.start()

    def log(self, message, level=logging.INFO):
        frame = inspect.currentframe().f_back
        filename = inspect.getfile(frame).split("/")[-1]
        line_number = frame.f_lineno
        function_name = frame.f_code.co_name
        log_message = f"[{filename}: {line_number}, {function_name}] {message}"
        self.log_queue.put((log_message, level))

    def _flush_logs(self):
        while True:
            time.sleep(self.flush_interval)
            while not self.log_queue.empty():
                message, level = self.log_queue.get()
                self.logger.log(level, message)

    def shutdown(self):
        self.log_process.terminate()
        self.log_process.join()
