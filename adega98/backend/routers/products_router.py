from __future__ import annotations

import fastapi

from ..core import utils
from ..models.users_model import User
from ..core.application import Application
from ..models.products_model import Product

app = Application.get_app()


async def validate_user(r: fastapi. Request):
    user_id = 1
    user = await User.get_by_id(user_id)
    if user.rule != "admin":
        print("Client error")


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
    
    return {
        "status": "ok", 
        "data": utils.get_partial_product_data(product)
    }