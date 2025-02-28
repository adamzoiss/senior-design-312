import logging
from logging.handlers import RotatingFileHandler
from src.utils.utils import get_proj_root, Path


def setup_logger(
    name=f"{__name__}", log_file="logs/project.log", overwrite=False
):
    # Clear log file
    if overwrite:
        with open(log_file, "w"):
            pass

    # Logger object
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a rotating file handler (max 5MB per file, keep last 5 logs)
    file_handler = RotatingFileHandler(
        f"{log_file}", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    # Set formatters
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger()
    logger.debug("This is a DEBUG message (will not show in terminal)")
    logger.info("This is an INFO message (will show in terminal)")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
