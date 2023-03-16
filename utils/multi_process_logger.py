import logging
import sys
import inspect
from pathlib import Path


class MultiProcessLogger:
    """
    A multi-process logger class that handles logging messages to both the console and a file.

    Attributes:
        log_level (int): The logging level.
        log_file (Path): The path to the log file.
        logger (logging.Logger): The logging instance.
    """

    def __init__(
        self,
        log_level=logging.INFO,
        log_file: Path = None,
    ):
        """
        Initialize the MultiProcessLogger object.

        Args:
            log_level (int, optional): The logging level. Defaults to logging.INFO.
            log_file (Path, optional): The path to the log file. Defaults to None.
        """
        self.log_level = log_level
        self.log_file = log_file

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)
        self.logger.propagate = False

        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)06d] [%(levelname)s] %(message)s",
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

    def log(self, message, level=logging.INFO):
        """
        Log the given message at the specified level.

        Args:
            message (str): The message to be logged.
            level (int, optional): The logging level. Defaults to logging.INFO.
        """
        frame = inspect.currentframe().f_back
        filename = inspect.getfile(frame).split("/")[-1]
        line_number = frame.f_lineno
        function_name = frame.f_code.co_name
        log_message = f"[{filename}: {line_number}, {function_name}] {message}"
        self.logger.log(level, log_message)

    def shutdown(self):
        """
        Shutdown the logger and close all associated handlers.
        """
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
