import logging
import sys
import inspect
from pathlib import Path
import datetime
import multiprocessing


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            formatted_time = dt.strftime(datefmt)
            # Add microseconds to the formatted time
            formatted_time += f".{int(record.msecs * 1000):06}"
        else:
            formatted_time = dt.strftime(self.default_time_format)
            formatted_time += f".{int(record.msecs * 1000):06}"
        return formatted_time


class LoggingProcess(multiprocessing.Process):
    def __init__(
        self, log_queue, log_level=logging.INFO, log_file: Path = None
    ):
        super().__init__()
        self.log_queue = log_queue
        self.log_level = log_level
        self.log_file = log_file

    def run(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level)
        logger.propagate = False

        formatter = CustomFormatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(self.log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if self.log_file:
            if self.log_file.exists():
                self.log_file.unlink()
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        while True:
            record = self.log_queue.get()
            if record == "shutdown":
                break
            logger.log(record["level"], record["message"])

        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)


class MultiProcessLogger:
    def __init__(
        self, log_queue, log_level=logging.INFO, log_file: Path = None
    ):
        self.log_queue = log_queue
        self.log_level = log_level
        self.log_file = log_file

    def log(self, message, level=logging.INFO):
        frame = inspect.currentframe().f_back
        filename = inspect.getfile(frame).split("/")[-1]
        line_number = frame.f_lineno
        function_name = frame.f_code.co_name
        log_message = f"[{filename}: {line_number}, {function_name}] {message}"
        record = {"level": level, "message": log_message}
        self.log_queue.put(record)


# class MultiProcessLogger:
#     """
#     A multi-process logger class that handles logging messages to both the console and a file.

#     Attributes:
#         log_level (int): The logging level.
#         log_file (Path): The path to the log file.
#         logger (logging.Logger): The logging instance.
#     """

#     def __init__(
#         self,
#         log_level=logging.INFO,
#         log_file: Path = None,
#     ):
#         """
#         Initialize the MultiProcessLogger object.

#         Args:
#             log_level (int, optional): The logging level. Defaults to logging.INFO.
#             log_file (Path, optional): The path to the log file. Defaults to None.
#         """
#         self.log_level = log_level
#         self.log_file = log_file

#         self.logger = logging.getLogger(__name__)
#         self.logger.setLevel(self.log_level)
#         self.logger.propagate = False

#         formatter = CustomFormatter(
#             "[%(asctime)s] [%(levelname)s] %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#         )

#         ch = logging.StreamHandler(sys.stdout)
#         ch.setLevel(self.log_level)
#         ch.setFormatter(formatter)
#         self.logger.addHandler(ch)

#         if self.log_file:
#             if self.log_file.exists():
#                 self.log_file.unlink()
#             file_handler = logging.FileHandler(self.log_file)
#             file_handler.setLevel(self.log_level)
#             file_handler.setFormatter(formatter)
#             self.logger.addHandler(file_handler)

#     def log(self, message, level=logging.INFO):
#         """
#         Log the given message at the specified level.

#         Args:
#             message (str): The message to be logged.
#             level (int, optional): The logging level. Defaults to logging.INFO.
#         """
#         frame = inspect.currentframe().f_back
#         filename = inspect.getfile(frame).split("/")[-1]
#         line_number = frame.f_lineno
#         function_name = frame.f_code.co_name
#         log_message = f"[{filename}: {line_number}, {function_name}] {message}"
#         self.logger.log(level, log_message)

#     def shutdown(self):
#         """
#         Shutdown the logger and close all associated handlers.
#         """
#         for handler in self.logger.handlers:
#             handler.close()
#             self.logger.removeHandler(handler)
