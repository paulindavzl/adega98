from __future__ import annotations

import os
import logging
import datetime as dt
import zoneinfo as zi
from decimal import Decimal
from typing import TYPE_CHECKING, overload

from .constants import LOGS_PATH

if TYPE_CHECKING:
    from ..models.users_model import User
    from ..models.stock_model import Stock
    from ..models.products_model import Product
    from .types import (
        FullStockData,
        FullProductData,
        PartialProductData,
        ValidateStringReturn,
    )


def validate_string(value: str, min_length: None|int=None, max_length: None|int=None) -> None|ValidateStringReturn:
    if not isinstance(value, str):
        return "not_string"
    if min_length is not None and len(value) < min_length:
        return "min_length_fail"
    if max_length is not None and len(value) > max_length:
        return "max_length_fail"
    

# retorna datetime de um UNIX
def get_datetime(unix: int|float) -> dt.datetime:
    _dt = dt.datetime.fromtimestamp(unix, tz=zi.ZoneInfo("America/Sao_Paulo"))
    return _dt


# retorna informações parciais do produto
def get_partial_product_data(p: Product) -> PartialProductData:
    return {
        "product_id": p.product_id,
        "name": p.name,
        "brand": p.brand,
        "category": p.category,
        "selling_price": p.selling_price,
        "image": p.image,
        "current_stock": p.stock.current_stock,
        "status": p.stock.status
    }


# retorna todas as informações uteis relacionadas ao produto
def get_full_product_data(p: Product) -> FullProductData:
    return {
        "product_id": p.product_id,
        "name": p.name,
        "brand": p.brand,
        "category": p.category,
        "description": p.description,
        "acquisition_price": p.acquisition_price,
        "selling_price": p.selling_price,
        "prefit_margin": p.prefit_margin,
        "prefit_margin_percent": p.prefit_margin_percent,
        "created_by": {
            "user_id": p.user.user_id,
            "name": p.user.name
        },
        "created_at": str(get_datetime(p.created_at)),
        "image": p.image,
        "current_stock": p.stock.current_stock,
        "pack": p.pack,
        "status": p.stock.status
    }


# retorna todas as informações uteis sobre o estoque
def get_full_stock_data(p: Product) -> FullStockData:
    return {
        "stock_id": p.stock.stock_id,
        "current_stock": p.stock.current_stock,
        "minimum_stock": p.stock.minimum_stock,
        "maximum_stock": p.stock.maximum_stock,
        "last_update": get_datetime(p.stock.last_update),
        "last_update_by": {
            "user_id": p.user.user_id,
            "name": p.user.name
        },
        "total_acquisition_price": p.stock.total_acquisition_price,
        "total_selling_price": p.stock.total_selling_price,
        "prefit_margin": p.stock.total_selling_price * p.prefit_margin_percent,
        "name": p.name,
        "brand": p.brand,
        "category": p.category,
        "description": p.description,
        "pack": p.pack,
        "image": p.image,
        "prefit_margin_percent": p.prefit_margin_percent,
        "created_at": get_datetime(p.created_at),
        "created_by": {
            "user_id": p.user.user_id,
            "name": p.user.name
        },
        "status": p.stock.status
    }


# formata um float para str (monetário)
def decimal_to_str(v: float|Decimal) -> str:
    return f"{v:.2f}".replace(".", ",")


# formata um str para float (monetário)
def str_to_decimal(v: str) -> Decimal:
    return Decimal(v.replace(",", "."))


# limpa os logs (modo dev ou tests)
def clean_logs(mode: str):
    logging.shutdown()
    log_path = os.path.join(LOGS_PATH, mode)
    if os.path.exists(log_path):
        for log_file in os.listdir(log_path):
            os.remove(os.path.join(log_path, log_file))
        
        os.rmdir(log_path)