import fastapi

from ..core import utils
from ..models.stock_model import Stock
from ..core.application import Application
from ..models.products_model import Product

app = Application.get_app()
products_router = app.get_router("products")


@products_router.post("/new")
async def new_product(
    request: fastapi.Request,
    name: str=fastapi.Form,
    category: str=fastapi.Form,
    brand: str=fastapi.Form,
    barcode: str|None = fastapi.Form(None),
    description: str=fastapi.Form,
    acquisition_price: float=fastapi.Form,
    selling_price: float=fastapi.Form,
    current_stock: int=fastapi.Form(0),
    minimum_stock: int=fastapi.Form(0),
    maximum_stock: int=fastapi.Form(None),
    pack: int=fastapi.Form(1),
): 
    product = await Product(
        name=name,
        category=category,
        brand=brand,
        barcode=barcode,
        description=description,
        acquisition_price=acquisition_price,
        selling_price=selling_price,
        created_by=0,
        pack=pack
    ).new(0, current_stock, minimum_stock, maximum_stock)
    
    return {
        "status": "ok", 
        "data": utils.get_partial_product_data(product)
    }