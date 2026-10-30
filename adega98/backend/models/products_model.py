from __future__ import annotations

import time
from decimal import Decimal
from typing import Literal, overload, ClassVar
from sqlalchemy import String, Integer, Numeric, select, func, ForeignKey 
from sqlalchemy.orm import mapped_column, Mapped, ColumnProperty, InstrumentedAttribute 

from . import Base
from ..core import utils
from .users_model import User
from .stock_model import Stock
from ..core.application import Application
from ..core.exceptions import ProductsDatabaseError
from ..core.constants import (
    INVALID_RETURNS_TYPE,
    MAX_LENGTH_PRODUCT_NAME,
)


app = Application.get_app()


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(MAX_LENGTH_PRODUCT_NAME), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    barcode: Mapped[None|str] = mapped_column(String(255), nullable=True, unique=True)
    description: Mapped[str] = mapped_column(String(), nullable=False)
    pack: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    acquisition_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False, default="/images/unknown-product.png")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    stock: ClassVar[Stock] = None
    user: ClassVar[User] = None


    # cria um novo produto
    async def new(self, current_stock: int=0, minimum_stock: int=0, maximum_stock: None|int=None) -> Product:
        await self.validate()
        
        async with app.session_local() as db:
            self.created_by = self.created_by.user_id
            self.created_at = int(time.time())
            db.add(self)
            await db.flush()

            stock = await Stock(
                stock_id=self.product_id,
                current_stock=current_stock,
                minimum_stock=minimum_stock,
                maximum_stock=maximum_stock,
                last_update_by=self.created_by
            ).new()

            db.add(stock)

            await db.commit()
            await db.refresh(self)
            await db.refresh(stock)
            await self._set_stock_user()
               
        return self
    

    # valida o produto para adicioná-lo ao db
    async def validate(self): pass


    # obtém registros de produtos
    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["all"], order_by: None|ColumnProperty[bool]=None) -> list[Product]: ...

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["one"],  order_by: None|ColumnProperty[bool]=None) -> Product: ...

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["first"],  order_by: None|ColumnProperty[bool]=None) -> None|Product: ...

    @overload
    @classmethod
    async def get(cls, *where, scalar: Literal["one_or_none"]) -> None|Product: ...
    
    @classmethod
    async def get(cls, *where, scalar: Literal["all", "one", "one_or_none", "first"], order_by: None|ColumnProperty[bool]=None):
        _select = select(cls)
        if where:
            _select = _select.where(*where)
        if order_by is not None:
            _select = _select.order_by(order_by)
        async with app.session_local() as db:
            query = await db.execute(_select)

            if scalar == "all": return [
                await p._set_stock_user() 
                for p in query.scalars().all() 
                if p is not None
            ]
            elif scalar == "first": 
                prod = query.scalars().first()
                if prod is not None:
                    return await prod._set_stock_user()
            elif scalar == "one": return query.scalar_one()._set_stock_user()
            elif scalar == "one_or_none": 
                prod = query.scalar_one_or_none()
                if prod is not None:
                    return await prod._set_stock_user()

    
    # obtém o usuário e o estoque
    async def _set_stock_user(self):
        self.stock, self.user = (
            await Stock.get_by_id(self.product_id),
            await User.get_by_id(self.created_by)
        )
        return self


    @classmethod
    async def get_by_id(cls, product_id: int) -> None|Product:
        return await cls.get(
            Product.product_id == product_id,
            scalar="one_or_none"
        )
    

    @classmethod
    async def get_by_name(cls, name: str) -> list[Product]:
        return await cls.get(
            Product.name == name,
            scalar="all",
            order_by=Product.created_at
        )
    

    @classmethod
    async def get_by_barcode(cls, barcode: str) -> None|Product:
        return await cls.get(
            Product.barcode == barcode,
            scalar="first",
            order_by=Product.created_at.asc()
        )
    

    @classmethod
    async def get_by_category(cls, category: str) -> list[Product]:
        return await cls.get(
            Product.category == category,
            scalar="all",
            order_by=Product.name.asc()
        )
    

    @classmethod
    async def get_by_brand(cls, brand: str) -> list[Product]:
        return await cls.get(
            Product.brand == brand,
            scalar="all",
            order_by=Product.name.asc()
        )


    @classmethod
    async def count(cls, *where) -> int:
        _select = select(func.count()).select_from(cls)
        if where:
            _select = _select.where(*where)
        async with app.session_local() as db:
            query = await db.execute(_select)
            return query.scalar_one()
        

    # retorna os valores de uma única coluna e quantas vezes ele repete
    @classmethod
    async def _get_columns_count(cls, column: InstrumentedAttribute) -> dict[str, int]:
        async with app.session_local() as db:
            query = await db.execute(select(column))
            categories = query.scalars().all()
            response = {}
            for c in set(categories):
                response[c] = categories.count(c)
            return response
        

    # retorna todas as categorias dos produtos
    @classmethod
    async def get_categories(cls) -> dict[str, int]:
        return await cls._get_columns_count(Product.category)
        

    # retorna todas as marcas dos produtos
    @classmethod
    async def get_brands(cls) -> dict[str, int]:
        return await cls._get_columns_count(Product.brand)
        

    # retorna a margem de lucro
    def _prefit_margin(self, percent: bool=False) -> Decimal:
        _sell_price = Decimal(str(self.selling_price))
        _acqui_price = Decimal(str(self.acquisition_price))

        margin = _sell_price - _acqui_price
        return (margin / _sell_price) if percent else margin
    

    @property
    def prefit_margin(self) -> Decimal:
        return self._prefit_margin(False)
    
    
    @property
    def prefit_margin_percent(self):
        return self._prefit_margin(True)
    

    def __str__(self):
        return f"{self.name} ({self.brand}{(" - " + self.barcode) if self.barcode else ""}): R$ {utils.decimal_to_str(self.selling_price)} ({utils.decimal_to_str(self.prefit_margin_percent * 100)}% pf)"