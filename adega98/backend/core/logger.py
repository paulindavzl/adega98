import os
import dotenv
import logging
from typing import TYPE_CHECKING
from logging.handlers import TimedRotatingFileHandler

from . import utils
from .exceptions import Adega98Exceptions, LoggerError
from .constants import (
    LOGS_PATH,
    ENVFILE_PATH,
    LOGS_NOT_DEFINED
)

if TYPE_CHECKING:
    from ..models.logs_model import Logs


dotenv.load_dotenv(ENVFILE_PATH)
MODE = os.getenv("MODE")
log_path = LOGS_PATH
if MODE is not None and MODE != "prod":
    log_path = os.path.join(LOGS_PATH, MODE)


# classe responsável por gerenciar Logs
class Logger(logging.Logger):
    def __init__(self, name: str, level: int=logging.INFO, logs: None|Logs=None):
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        
        super().__init__(name)
        self.setLevel(level)
        self.propagate = False
        self.logs = logs

        self.set_handlers()
        
    
    # define os handlers (se não existir)
    def set_handlers(self):
        if not self.handlers:
            handler = TimedRotatingFileHandler(
                filename=os.path.join(log_path, "adega98.log"),
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
    async def new_exception_log(self, exc: Adega98Exceptions) -> None|Logs:
        if self.logs is None:
            self.critical(LOGS_NOT_DEFINED)
            raise LoggerError(
                cause="logger_not_defined",
                log_level="CRITICAL",
                message=LOGS_NOT_DEFINED,
                status_code=500
            )
        
        level = exc.log_level
        super().log(
            logging.getLevelName(level), 
            exc.message, 
            exc_info=(
                type(exc),
                exc,
                exc.__traceback__
            ) if exc is not None else exc
        )

        # se o log for grave, salva no banco de dados para permitir consulta posteriormente
        if exc.log_level in ["ERROR", "CRITICAL"]:
            log = Logs(
                level = level,
                logger_name = self.name,
                message = exc.message,
                timestamp = utils.get_datetime(exc.time).isoformat(),
                user_id = exc.content.get("user_id"),
                http_method = exc.content.get("http_method"),
                http_path = exc.content.get("http_path"),
                http_code = exc.status_code,
                exc=exc
            )
            return await log.add()