from __future__ import annotations

from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column

from . import Base
from ..core.application import Application


app = Application.get_app()


class Logs(Base):
    __tablename__ = "logs"

    # informações gerais
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String, nullable=False)
    logger_name: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)

    # informações http (opcionais)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    http_method: Mapped[str] = mapped_column(String, nullable=True)
    http_path: Mapped[str] = mapped_column(String, nullable=True)
    http_code: Mapped[int] = mapped_column(Integer, nullable=True)

    # informações de exceções (opcionais)
    exception_type: Mapped[str] = mapped_column(String, nullable=True)
    exception_name: Mapped[str] = mapped_column(String, nullable=True)
    exception_cause: Mapped[str] = mapped_column(String, nullable=True)
    exception_traceback: Mapped[str] = mapped_column(String, nullable=True)


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