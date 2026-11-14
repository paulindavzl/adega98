from __future__ import annotations

import io
import os
import PIL
import PIL.Image
import fastapi
import logging
import datetime as dt
import zoneinfo as zi
from decimal import Decimal
from typing import TYPE_CHECKING, overload

from .exceptions import Adega98Exceptions, ProductRouterError
from .constants import (
    LOGS_PATH,
    INVALID_IMAGE,
    MAX_IMAGE_SIZE,
    PRODUCT_FILES_PATH,
    IMAGE_WITHOUT_CONTENT,
    MAX_IMAGE_SIZE_EXT_MB,
    IMAGE_DIMENSION_PIXELS,
    INVALID_IMAGE_EXTENSION,
    MAX_IMAGE_SIZE_EXCEEDED,
    IMAGE_ALLOWEDS_EXTENSIONS,
)

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
        "name": p.name.title(),
        "brand": p.brand.title(),
        "category": p.category.title(),
        "selling_price": p.selling_price,
        "image": str(p.image),
        "current_stock": p.stock.current_stock,
        "status": p.stock.status
    }


# retorna todas as informações uteis relacionadas ao produto
def get_full_product_data(p: Product) -> FullProductData:
    return {
        "product_id": p.product_id,
        "name": p.name.title(),
        "brand": p.brand.title(),
        "category": p.category.title(),
        "description": p.description.capitalize(),
        "acquisition_price": p.acquisition_price,
        "selling_price": p.selling_price,
        "prefit_margin": p.prefit_margin,
        "prefit_margin_percent": p.prefit_margin_percent,
        "created_by": {
            "user_id": p.user.user_id,
            "name": p.user.name.title()
        },
        "created_at": str(get_datetime(p.created_at)),
        "image": str(p.image),
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
            "name": p.user.name.title()
        },
        "total_acquisition_price": p.stock.total_acquisition_price,
        "total_selling_price": p.stock.total_selling_price,
        "prefit_margin": p.stock.total_selling_price * p.prefit_margin_percent,
        "name": p.name.title(),
        "brand": p.brand.title(),
        "category": p.category.title(),
        "description": p.description.capitalize(),
        "pack": p.pack,
        "image": str(p.image),
        "prefit_margin_percent": p.prefit_margin_percent,
        "created_at": get_datetime(p.created_at),
        "created_by": {
            "user_id": p.user.user_id,
            "name": p.user.name.title()
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


# reduz o tamanho da imagem (800x800px)
def process_image(content: bytes, raiser: Adega98Exceptions) -> bytes:
    if not content:
        raise raiser(
            cause="image_without_content",
            message=IMAGE_WITHOUT_CONTENT,
            status_code=422,
            log_level="ERROR",
            save_in_database=True
        )
    
    if len(content) > MAX_IMAGE_SIZE:
        raise raiser(
            cause="max_image_size_exceeded",
            message=MAX_IMAGE_SIZE_EXCEEDED,
            status_code=422,
            log_level="ERROR",
            content={
                "max_image_size": f"{MAX_IMAGE_SIZE_EXT_MB}mb"
            },
            save_in_database=True
        )
    
    image = PIL.Image.open(io.BytesIO(content))
    if image.format not in IMAGE_ALLOWEDS_EXTENSIONS:
        raise raiser(
            cause="invalid_image_extension",
            message=INVALID_IMAGE_EXTENSION,
            status_code=422,
            log_level="ERROR",
            content={
                "extensions": IMAGE_ALLOWEDS_EXTENSIONS,
                "extension_used": image.format
            },
            save_in_database=True
        )
    
    image.verify()
    image = PIL.Image.open(io.BytesIO(content))
    
    image.thumbnail(IMAGE_DIMENSION_PIXELS, PIL.Image.Resampling.LANCZOS)
    if image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
    
    output = io.BytesIO()
    image.save(
        output,
        format="WEBP",
        quality=85,
        method=6
    )

    return output.getvalue()


# salva uma imagem
async def save_image(image: fastapi.UploadFile, filename: str):
    content: bytes
    try:
        content = process_image(await image.read(MAX_IMAGE_SIZE + 1), ProductRouterError)
    except (PIL.UnidentifiedImageError):
        raise ProductRouterError(
            cause="invalid_image",
            message=INVALID_IMAGE,
            status_code=422,
            log_level="ERROR",
            save_in_database=True
        )

    file_path = os.path.join(PRODUCT_FILES_PATH, filename)
    with open(file_path, "wb") as file:
        file.write(content)


# apaga uma imagem
def delete_image(filename: str):
    file_path = os.path.join(PRODUCT_FILES_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


# obtém todos os caminhos das imagens
def get_images_name() -> list[str]:
    return os.listdir(PRODUCT_FILES_PATH)
    

def regularize_str(value: str) -> str:
    return " ".join(value.split()).lower().strip()