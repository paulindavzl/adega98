from typing import Any

class Adega98Exceptions(Exception):
    error_name: str
    cause: str
    message: str
    status_code: int
    content: None|dict[str, Any]

    def __init__(self, cause: str, message: str, status_code: None|int=None, content: None|dict[str, Any]=None):
        self.cause = cause
        self.message = message
        self.content = content
        if status_code:
            self.status_code = status_code

        if content is not None:
            for k, v in content.items():
                message += f"\n{k}: {v}"
        super().__init__(message)


class EnvError(Adega98Exceptions):
    error_name = "env_error"
    status_code = 500


class ProductsDatabaseError(Adega98Exceptions):
    error_name = "products_database_error"