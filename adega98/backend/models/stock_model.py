from __future__ import annotations

import time
from decimal import Decimal
from typing import TYPE_CHECKING, overload, Literal
from sqlalchemy import Integer, ForeignKey, Boolean, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..core.application import Application

if TYPE_CHECKING:
    from .products_model import Product


app = Application.get_app()


class Stock(Base):
    __tablename__ = "stock"

    stock_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, unique=True, primary_key=True)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minimum_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    maximum_stock: Mapped[int] = mapped_column(Integer, nullable=True)

    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_update: Mapped[int] = mapped_column(Integer, nullable=False)
    last_update_by: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # cria um novo estoque
    async def new(self):
        self.last_update = int(time.time())
        return self
    

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["one"]) -> Stock: ...

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["one_or_none"]) -> None|Stock: ...

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["first"]) -> None|Stock: ...

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["all"]) -> list[Stock]: ...

    @classmethod
    async def get(cls, *where, scalar: Literal["one", "one_or_none", "first", "all"]) -> None|Stock|list[Stock]:
        async with app.session_local() as db:
            _select = select(Stock)
            if where:
                _select = _select.where(*where)
            query = await db.execute(_select)
            
            if scalar == "all": return query.scalars().all()
            elif scalar == "first": return query.scalars().first()
            elif scalar == "one": return query.scalar_one()
            elif scalar == "one_or_none": return query.scalar_one_or_none()
    

    # obtém um estoque pelo id
    @classmethod
    async def get_by_id(cls, stock_id: int) -> None|Stock:
        return await cls.get(
            Stock.stock_id == stock_id,
            scalar="one_or_none"
        )
    

    @property
    def total_selling_price(self) -> Decimal:
        return Decimal(str(self.product.selling_price * self.current_stock))
    
    @property
    def total_acquisition_price(self) -> Decimal:
        return Decimal(str(self.product.acquisition_price * self.current_stock))
    