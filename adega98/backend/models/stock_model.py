from __future__ import annotations

import time
from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, Boolean, select
from typing import TYPE_CHECKING, overload, Literal, ClassVar
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..core.logger import Logger
from ..core.application import Application

if TYPE_CHECKING:
    from .products_model import Product


app = Application.get_app()
logger = Logger(__name__)


class Stock(Base):
    __tablename__ = "stock"

    stock_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, unique=True, primary_key=True)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minimum_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    maximum_stock: Mapped[int] = mapped_column(Integer, nullable=True)

    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_update: Mapped[int] = mapped_column(Integer, nullable=False)
    last_update_by: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    product: ClassVar[None|Product] = None


    # cria um novo estoque
    async def new(self, product: Product):
        self.last_update = int(time.time())
        self.product = product

        return self
    

    @classmethod
    async def get_by_id(cls, stock_id: int, product: Product) -> None|Stock:
        async with app.session_local() as db:
            query = await db.execute(select(cls).where(Stock.stock_id == stock_id))
            stock = query.scalar_one_or_none()
            stock.product = product
            return stock
    

    @property
    def total_selling_price(self) -> Decimal:
        return Decimal(str(self.product.selling_price * self.current_stock))
    
    @property
    def total_acquisition_price(self) -> Decimal:
        return Decimal(str(self.product.acquisition_price * self.current_stock))
    