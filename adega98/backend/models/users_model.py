from __future__ import annotations

import time
from typing import Literal
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, select, Numeric

from . import Base
from ..core.application import Application


app = Application.get_app()


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    whatsapp: Mapped[str] = mapped_column(String(11), nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=True)
    rule: Mapped[str] = mapped_column(String(6), nullable=False, default="client")
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    delay_fine: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=True)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)


    async def new(self):
        async with app.session_local() as db:
            self.created_at = int(time.time())

            db.add(self)
            await db.commit()
            await db.refresh(self)
        
        return self
    

    # obtém um usuário pelo ID
    @classmethod
    async def get_by_id(cls, user_id: int) -> User|None:
        async with app.session_local() as db:
            query = await db.execute(select(User).where(User.user_id == user_id))
            return query.scalar_one_or_none()