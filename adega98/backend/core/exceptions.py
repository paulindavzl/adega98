import time
from typing import Any, TYPE_CHECKING

from .types import LogLevel


class Adega98Exceptions(Exception):
    error_name: str = "adega98_base_exceptions"
    cause: str
    message: str
    status_code: int
    content: dict[str, Any]
    log_level: None|LogLevel
    module_name: str
    time: int

    def __init__(self, cause: str, message: str, status_code: None|int=None, content: dict[str, Any]={}, log_level: None|LogLevel=None):
        self.cause = cause
        self.message = message
        self.content = content
        self.log_level = log_level
        self.module_name = __name__
        self.time = int(time.time())
        if status_code:
            self.status_code = status_code

        for k, v in content.items():
            message += f"\n{k}: {v}"
        super().__init__(message)


    @classmethod
    def convert(cls, exc: Exception) -> "Adega98Exceptions":
        return Adega98Exceptions(
            cause="internal_error",
            message=str(exc),
            content={},
            log_level="CRITICAL",
            status_code=500
        )


class EnvError(Adega98Exceptions):
    error_name = "env_error"
    status_code = 500


class ProductsDatabaseError(Adega98Exceptions):
    error_name = "products_database_error"


class LogsDatabaseError(Adega98Exceptions):
    error_name = "logs_database_error"