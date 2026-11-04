import os
import logging
from logging.handlers import TimedRotatingFileHandler

from . import utils
from .constants import LOGS_PATH
from ..models.logs_model import Logs
from .exceptions import Adega98Exceptions


# classe responsável por gerenciar Logs
class Logger(logging.Logger):
    def __init__(self, name: str):
        if not os.path.join(LOGS_PATH):
            os.makedirs(LOGS_PATH, exist_ok=True)
        
        super().__init__(name)
        self.setLevel(logging.INFO)
        self.propagate = False

        self.set_handlers()

    
    # define os handlers (se não existir)
    def set_handlers(self):
        if not self.handlers:
            handler = TimedRotatingFileHandler(
                filename=os.path.join(LOGS_PATH, "adega98.log"),
                when="midnight",
                interval=1,
                backupCount=7,
                utc=False,
                encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "$asctime | $levelname | $name | $message | $pathname:$module:$lineno ($funcName) | $process",
                datefmt="%d/%m/%Y - %H:%M:%S",
                style="$"
            ))

            self.addHandler(handler)


    # adiciona um novo log com base na exceção e pode adicionar no banco de dados
    async def new_log(self, exc: Adega98Exceptions) -> Logs:
        level = exc.log_level
        super().log(
            level, 
            exc.message, 
            exc_info=(
                type(exc),
                exc,
                exc.__traceback__
            ) if exc is not None else exc
        )

        if level in ["ERROR", "CRITICAL"]:
            log = Logs(
                level = level,
                logger_name = self.name,
                message = exc.message,
                timestamp = utils.get_datetime(exc.time),
                user_id = exc.content.get("user_id"),
                http_method = exc.content.get("http_method"),
                http_path = exc.content.get("http_path"),
                http_code = exc.status_code,
                exception_type = type(exc).__name__,
                exception_name = exc.error_name,
                exception_cause = exc.cause,
                exception_traceback = exc.__traceback__,
            )
            return await log.add()