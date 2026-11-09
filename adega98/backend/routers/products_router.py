from __future__ import annotations

import fastapi

from ..core import utils
from ..core.logger import Logger
from ..models.users_model import User
from ..core.application import Application
from ..models.products_model import Product


app = Application.get_app()
logger = Logger(__name__)


async def validate_user(r: fastapi. Request):
    user_id = 1
    user = await User.get_by_id(user_id)
    if user.rule != "admin":
        print("Client error")
        logger.error(f"user ({user.name} - id: {user.user_id}) does not have authorization for this route ({r.url.path})")


products_router = app.get_router("products", [fastapi.Depends(validate_user)])


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
    pack: int=fastapi.Form(1)
): 
    user_id = 1
    user = await User.get_by_id(user_id)
    logger.info(f"user {user.name} (id: {user.user_id}) requested the creation of a new product ({name})")

    product = await Product(
        name=name,
        category=category,
        brand=brand,
        barcode=barcode,
        description=description,
        acquisition_price=acquisition_price,
        selling_price=selling_price,
        created_by=user,
        pack=pack
    ).new(current_stock, minimum_stock, maximum_stock)
    
    logger.info(f"product (name: {product.name} - product id: {product.product_id}) successfully created by {user.name} (id: {user.user_id})")
    return {
        "status": "ok", 
        "data": utils.get_partial_product_data(product)
    }