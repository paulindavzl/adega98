import fastapi
from typing import TYPE_CHECKING

from ..core.logger import Logger
from ..models.logs_model import Logs
from ..core.application import Application
from ..core.exceptions import Adega98Exceptions
from ..core.constants import (
    JS_PATH,
    CSS_PATH,
    FONTS_PATH,
    IMAGES_PATH,
    INTERNAL_ERROR,
    TEMPLATES_PATH,
)

if TYPE_CHECKING:
    from ..core.types import HTTPErrorResponse


app = Application.get_app()
logger = Logger(__name__)


# monta rotas estáticas
app.mount(
    js=JS_PATH,
    css=CSS_PATH,
    fonts=FONTS_PATH,
    images=IMAGES_PATH,
    templates=TEMPLATES_PATH
)

# cria a página fixa do sistema
@app.get("/")
async def index(r: fastapi.Request):
    return app.render(r, "index.html")


# captura os erros e retorna uma mensagem de erro
@app.exception_handler(Exception)
async def exception_handler(r: fastapi.Request, exc: Adega98Exceptions) -> fastapi.responses.JSONResponse:
    response: HTTPErrorResponse
    _pe: bool
    if isinstance(exc, Adega98Exceptions):
        _pe = True
        response = {
            "cause": exc.cause,
            "content": exc.content,
            "error_name": exc.error_name,
            "message": exc.message,
            "status_code": exc.status_code,
            "log_level": exc.log_level
        }
    else:
        _pe = False
        response = {
            "cause": "internal_error",
            "error_name": "internal_error",
            "log_level": "CRITICAL",
            "message": INTERNAL_ERROR,
            "status_code": 500
        }

    _ll = logger.warning if _pe else logger.error
    _ll(f"error captured (name: {response["error_name"]})")

    handler_logger = Logger(exc.module_name if _pe else "internal_error", logs=Logs)
    log = await handler_logger.new_exception_log(exc if _pe else Adega98Exceptions.convert(exc))
    if log is not None:
        response["log_id"] = log.log_id

    return fastapi.responses.JSONResponse(
        content=response,
        status_code=response["status_code"]
    )

        