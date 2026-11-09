from __future__ import annotations

import traceback
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, select, func

from . import Base
from ..core.application import Application
from ..core.exceptions import Adega98Exceptions, LogsDatabaseError
from ..core.constants import (
    EXCEPTION_NOT_INTERNAL_BASE
)


app = Application.get_app()


class Logs(Base):
    __tablename__ = "logs"

    # informações gerais
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String, nullable=False)
    logger_name: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)

    # informações de exceções
    exception_type: Mapped[str] = mapped_column(String, nullable=False)
    exception_name: Mapped[str] = mapped_column(String, nullable=False)
    exception_cause: Mapped[str] = mapped_column(String, nullable=False)
    exception_traceback: Mapped[str] = mapped_column(String, nullable=False)
    
    # informações http (opcionais)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    http_method: Mapped[str] = mapped_column(String, nullable=True)
    http_path: Mapped[str] = mapped_column(String, nullable=True)
    http_code: Mapped[int] = mapped_column(Integer, nullable=True)


    def __init__(self, exc: Adega98Exceptions, **kw):
        def _if_has_set(k: str, ov: Any, o: dict[str, Any]) -> bool:
            if k in kw.keys():
                o[k] = ov[k]
        
        if not isinstance(exc, Adega98Exceptions):
            err = LogsDatabaseError(
                cause="exception_not_internal_base",
                message=EXCEPTION_NOT_INTERNAL_BASE,
                status_code=500,
                log_level="CRITICAL"
            )
            _if_has_set("user_id", kw, err.content)
            _if_has_set("http_method", kw, err.content)
            _if_has_set("http_path", kw, err.content)
            _if_has_set("http_code", kw, err.content)

            raise err

        # obtém as informações da exceção (apenas base Adega98Exception)
        kw["exception_type"] = type(exc).__name__
        kw["exception_name"] = exc.error_name
        kw["exception_cause"] = exc.cause
        kw["exception_traceback"] = "".join(traceback.format_exception(
            type(exc),
            exc,
            exc.__traceback__
        ))
        
        super().__init__(**kw)


    # adiciona um log no banco de dados
    async def add(self):
        async with app.session_local() as db:
            db.add(self)
            await db.commit()
            await db.refresh(self)

            return self
        

    # obtém um log pelo ID
    @classmethod
    async def get_by_id(cls, log_id: int) -> None|Logs:
        async with app.session_local() as db:
            query = await db.execute(select(cls).where(Logs.log_id == log_id))
            return query.scalar_one_or_none()
        
    
    # obtém todos os logs pelo user_id
    @classmethod
    async def get_by_user(cls, user_id: int) -> list[Logs]:
        async with app.session_local() as db:
            query = await db.execute(select(cls).where(Logs.user_id == user_id))
            return query.scalars().all()


    # obtém todos os logs
    @classmethod
    async def get_all(cls) -> list[Logs]:
        async with app.session_local() as db:
            query = await db.execute(select(cls))
            return query.scalars().all()
        
    
    # retorna a quantidade de logs no banco de dados
    @classmethod
    async def count(cls) -> int:
        async with app.session_local() as db:
            query = await db.execute(select(func.count()).select_from(cls))
            return query.scalar()