import logging
from logging.handlers import RotatingFileHandler
from src.utils.constants import EN_CONSOLE_LOGGING


class Logger:
    _instances = {}

    def __new__(
        cls,
        name="app",
        log_file="logs/project.log",
        overwrite=False,
        console_level=logging.INFO,
        console_logging=EN_CONSOLE_LOGGING,
    ):
        """Singleton pattern: Ensures each logger instance is unique by name."""
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._setup_logger(
                name, log_file, overwrite, console_level, console_logging
            )
            # Store the actual logger instance
            cls._instances[name] = instance.logger

        # Return logging.Logger
        return cls._instances[name]

    def _setup_logger(
        self, name, log_file, overwrite, console_level, console_logging
    ):
        """Initializes the logger with file and console handlers."""
        if overwrite:
            with open(log_file, "w"):
                pass

        self.logger = logging.getLogger(name)
        # Capture all logs (file handler filters separately)
        self.logger.setLevel(logging.DEBUG)
        # Prevent duplicate handlers
        self.logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )

        # Console handler (optional)
        if console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Rotating file handler (captures everything)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
