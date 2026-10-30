from decimal import Decimal
from typing import Literal, TypedDict

ValidateStringReturn = Literal["not_string", "min_length_fail", "max_length_fail"]

class _UserTempType(TypedDict):
    user_id: int
    name: str

class PartialProductData(TypedDict):
    product_id: int
    name: str
    brand: str
    category: str
    selling_price: Decimal
    image: str
    pack: int

    # informações do estoque
    current_stock: int
    status: bool


class FullProductData(TypedDict):
    # informações do produto
    product_id: int
    name: str
    brand: str
    category: str
    acquisition_price: Decimal
    selling_price: Decimal
    prefit_margin: Decimal
    prefit_margin_percent: Decimal
    description: str
    created_at: str
    image: str
    created_by: _UserTempType

    # informações do estoque
    current_stock: int
    pack: int
    status: bool


class FullStockData(TypedDict):
    # informações do estoque
    stock_id: int
    current_stock: int
    minimum_stock: int
    maximum_stock: None|int
    status: bool
    last_update: str
    last_update_by: _UserTempType
    total_acquisition_price: Decimal
    total_selling_price: Decimal
    prefit_margin: Decimal

    # informações do produto
    name: str
    category: str
    brand: str
    description: str
    pack: int
    image: str
    created_by: _UserTempType
    created_at: str
    prefit_margin_percent: Decimal


