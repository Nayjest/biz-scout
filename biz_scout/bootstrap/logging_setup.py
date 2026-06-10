import logging
from datetime import datetime
import microcore as mc


def setup_logging(log_level: int = logging.INFO):
    """Setup custom CLI logging format with colored output."""

    class CustomFormatter(logging.Formatter):
        def format(self, record):
            dt = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
            message, level_name = record.getMessage(), record.levelname
            if record.levelno == logging.WARNING:
                message = mc.ui.yellow(message)
                level_name = mc.ui.yellow(level_name)
            if record.levelno >= logging.ERROR:
                message = mc.ui.red(message)
                level_name = mc.ui.red(level_name)

            formatted_message = f"{dt} {level_name}: {message}"
            if record.exc_info:
                formatted_message += "\n" + self.formatException(record.exc_info)
            return formatted_message

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=log_level, handlers=[handler])
