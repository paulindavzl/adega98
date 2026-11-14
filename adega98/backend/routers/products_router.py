from __future__ import annotations

import os
import uuid
import fastapi
from typing import Callable

from ..core import utils
from ..core.logger import Logger
from ..models.users_model import User
from ..core.application import Application
from ..models.products_model import Product
from ..core.exceptions import ProductRouterError
from ..core.constants import (
    IMAGES_PATH,
    PRODUCT_NOT_FOUND,
    PRODUCT_FILES_PATH,
    INVALID_GET_ALL_PRODUCT_SELECT,
    PRODUCT_IDENTIFIER_CANNOT_NONE,
    INVALID_PRODUCT_IDENTIFIER_VALUE,
)

app = Application.get_app()
logger = Logger(__name__)


products_router = app.get_router("products")


# adiciona um novo produto
@products_router.post("/new")
async def new_product(
    request: fastapi.Request,
    name: str=fastapi.Form(None),
    category: str=fastapi.Form(None),
    brand: str=fastapi.Form(None),
    barcode: str|None = fastapi.Form(None),
    description: str=fastapi.Form(None),
    acquisition_price: float=fastapi.Form(None),
    selling_price: float=fastapi.Form(None),
    current_stock: int=fastapi.Form(0),
    minimum_stock: int=fastapi.Form(0),
    maximum_stock: int=fastapi.Form(None),
    pack: int=fastapi.Form(1),
    image: fastapi.UploadFile=fastapi.File(None)
): 
    user_id = 1
    user = await User.get_by_id(user_id)
    logger.info(f"user {user.name} (id: {user.user_id}) requested the creation of a new product ({name})")

    filename: str = None
    if image is not None:
        filename = f"{str(uuid.uuid4())}.webp"

    product = await Product(
        name=utils.regularize_str(name),
        category=utils.regularize_str(category),
        brand=utils.regularize_str(brand),
        barcode=barcode,
        description=utils.regularize_str(description),
        acquisition_price=acquisition_price,
        selling_price=selling_price,
        created_by=user,
        pack=pack,
        image=filename
    ).new(current_stock, minimum_stock, maximum_stock)

    if image is not None:
        await utils.save_image(image, filename)
    
    logger.info(f"product (name: {product.name} - product id: {product.product_id}) successfully created by {user.name} (id: {user.user_id})")
    return {
        "status": "ok", 
        "data": {"product": utils.get_full_product_data(product)}
    }


# obtém todos os produtos
@products_router.get("/all")
async def get_all_products(
    request: fastapi.Request, select: str=None, value: str=None
):
    products: list[Product]
    if select is not None and value is not None:
        getter: Callable
        if select == "name": getter = Product.get_by_name
        elif select == "brand": getter = Product.get_by_brand
        elif select == "category": getter = Product.get_by_category
        else:
            raise ProductRouterError(
                cause="invalid_product_column",
                message=INVALID_GET_ALL_PRODUCT_SELECT,
                status_code=422,
                log_level="ERROR",
                content={
                    "columns_expected": ["name", "brand", "category"],
                    "column_received": select,
                    "user_id": 1,
                },
                save_in_database=False
            )
        
        products = await getter(value.lower())
    else:
        products = await Product.get(scalar="all", order_by=Product.created_at.asc())
    
    return {
        "status": "ok",
        "data": {
            "search_by": {
                "select": select if select is not None else "all",
                "value": value
            },
            "products": [utils.get_partial_product_data(product) for product in products]
        }
    }


# obtém um produto pelo identificador (ID ou barcode)
@products_router.get("/by")
async def get_product_by(request: fastapi.Request, identifier: str=None, value: int|str=None, full_data: bool=False):
    if identifier is None or value is None:
        raise ProductRouterError(
            cause="identifier_cannot_none",
            message=PRODUCT_IDENTIFIER_CANNOT_NONE,
            status_code=400,
            log_level="ERROR",
            content={
                "user_id": 1,
            },
            save_in_database=False
        )
    
    getter: Callable
    if identifier == "id": getter = Product.get_by_id
    elif identifier == "barcode": getter = Product.get_by_barcode
    else:
        raise ProductRouterError(
            cause="invalid_identifier_value",
            message=INVALID_PRODUCT_IDENTIFIER_VALUE,
            status_code=422,
            log_level="ERROR",
            content={
                "user_id": 1,
            },
            save_in_database=False
        )
    product = await getter(value)
    if product is None:
        raise ProductRouterError(
            cause="product_not_found",
            message=PRODUCT_NOT_FOUND,
            status_code=404,
            log_level="WARNING",
            content={
                "user_id": 1,
                "identifier": identifier,
                "value": value
            },
            save_in_database=False
        )
    product_data = utils.get_full_product_data if full_data else utils.get_partial_product_data
    return {
        "status": "ok",
        "data": {
            "search_by": {
                "identifier": identifier,
                "value": value
            },
            "product": product_data(product)
        }
    }


# atualiza as informações de um produto
@products_router.put("/update/{product_id}")
async def update_product(
    request: fastapi.Request,
    product_id: str,
    name: str=fastapi.Form(None),
    category: str=fastapi.Form(None),
    brand: str=fastapi.Form(None),
    barcode: str|None = fastapi.Form(None),
    description: str=fastapi.Form(None),
    acquisition_price: float=fastapi.Form(None),
    selling_price: float=fastapi.Form(None),
    current_stock: int=fastapi.Form(None),
    minimum_stock: int=fastapi.Form(None),
    maximum_stock: int=fastapi.Form(None),
    pack: int=fastapi.Form(None),
    image: fastapi.UploadFile=fastapi.File(None)

):
    user_id = 1
    product = await Product.get_by_id(product_id)
    if product is None:
        raise ProductRouterError(
            cause="product_not_found",
            message=PRODUCT_NOT_FOUND,
            status_code=404,
            log_level="WARNING",
            save_in_database=True,
            content={
                "user_id": user_id,
                "product_id": product_id
            }
        )
    product_image = product.image
    filename: str = None
    if image is not None:
        filename = f"{str(uuid.uuid4())}.webp"

    await product.update(
        user_id=user_id,
        name=name,
        category=category,
        brand=brand,
        barcode=barcode,
        description=description,
        acquisition_price=acquisition_price,
        selling_price=selling_price,
        pack=pack,
        image=filename,
        current_stock=current_stock,
        minimum_stock=minimum_stock,
        maximum_stock=maximum_stock
    )

    if product_image != filename:
        utils.delete_image(product_image)
    if image is not None:
        await utils.save_image(image, filename)
    
    return {
        "status": "ok",
        "data": {
            "user_id": user_id,
            "product": utils.get_full_product_data(product)
        }
    }


# retorna todas as categorias de produtos
@products_router.get("/categories")
async def get_product_categories(request: fastapi.Request):
    categories = await Product.get_categories()
    return {
        "status": "ok",
        "data": {"categories": categories}
    }


# retorna todas as marcas de produtos
@products_router.get("/brands")
async def get_product_brands(request: fastapi.Request):
    brands = await Product.get_brands()
    return {
        "status": "ok",
        "data": {"brands": brands}
    }


# retorna a imagem de um produto
@products_router.get("/image/{filename}")
async def get_product_image(request: fastapi.Request, filename :str):
    path = os.path.join(PRODUCT_FILES_PATH, filename)
    if not os.path.exists(path):
        path = os.path.join(IMAGES_PATH, "unknown-product.webp")
    return fastapi.responses.FileResponse(path)