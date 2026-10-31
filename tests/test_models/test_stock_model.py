import pytest
import pytest_asyncio

from adega98.backend.models.users_model import User
from adega98.backend.models.stock_model import Stock
from adega98.backend.models.products_model import Product


@pytest_asyncio.fixture
async def register_product(restart_database, user_instance: User):
    user = await user_instance.new()
    await Product(
        name=f"Test Product",
        category="Tests",
        brand="Testing",
        barcode=f"00000010",
        description="This is a test product",
        pack=2,
        acquisition_price=0.99,
        selling_price=1.99,
        created_by=user
    ).new(10, 1, 15)


@pytest.mark.asyncio
async def get_by_id(register_product):
    product = await Product.get_by_id(1)
    stock = await Stock.get_by_id(1, product)

    assert stock.product == product
    assert stock.current_stock == 10


@pytest.mark.asyncio
async def test_stock_model_total_selling_price(register_product):
    product = await Product.get_by_id(1)
    stock = await Stock.get_by_id(1, product)

    assert stock.total_selling_price == (stock.current_stock * product.selling_price)


@pytest.mark.asyncio
async def test_stock_model_total_acquisition_price(register_product):
    product = await Product.get_by_id(1)
    stock = await Stock.get_by_id(1, product)

    assert stock.total_acquisition_price == (stock.current_stock * product.acquisition_price)