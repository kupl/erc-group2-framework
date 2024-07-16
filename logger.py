import logging
import logging.handlers

from rich.logging import RichHandler

RICH_FORMAT = ">> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"

def set_logger(log_path) -> logging.Logger:
    logging.basicConfig(
        level="NOTSET",
        format=RICH_FORMAT,
        handlers=[RichHandler(show_time=False, rich_tracebacks=True)]
    )
    logger = logging.getLogger("rich")

    # file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    # file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    # logger.addHandler(file_handler)

    return logger