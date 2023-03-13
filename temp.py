import logging
from pathlib import Path
import time
from multi_process_logger import MultiProcessLogger


def main():
    logger = MultiProcessLogger(flush_interval=1e-4, log_file=Path("test.log"))
    logger.log("This is a test message", logging.INFO)
    time.sleep(2)
    logger.shutdown()


if __name__ == "__main__":
    main()
