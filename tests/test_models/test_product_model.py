import pytest

from adega98.backend.core import utils
from adega98.backend.models.users_model import User
from adega98.backend.models.products_model import Product


@pytest.mark.asyncio
async def test_product_model_new(restart_database, product_instance: Product):
    prod = await product_instance.new(
        current_stock=1
    )

    assert prod.product_id == 1
    assert prod.stock is not None
    assert prod.product_id == prod.stock.stock_id
    assert prod.user is not None
    assert prod.user.user_id == 1


@pytest.mark.asyncio
async def test_product_model_get_by_id(register_products):
    prod0 = await Product.get_by_id(0)
    prod1 = await Product.get_by_id(1)

    assert prod0 is None
    assert prod1 is not None
    assert prod1.product_id == 1


@pytest.mark.asyncio
async def test_product_model_get_by_name(register_products_delay):
    prods = await Product.get_by_name("Test Product")

    assert len(prods) == 10

    prod0 = prods[0]
    prod1 = prods[1]

    assert prod0.name == prod1.name
    assert prod0.created_at < prod1.created_at


@pytest.mark.asyncio
async def test_product_model_get_by_barcode(register_products):
    prod = await Product.get_by_barcode("00000010")
    prod_none = await Product.get_by_barcode("0")

    assert prod_none is None
    assert prod is not None


@pytest.mark.asyncio
async def test_product_model_get_by_category(register_products):
    prods = await Product.get_by_category("Tests")
    prods_none = await Product.get_by_category("Any")

    assert len(prods_none) == 0
    assert len(prods) == 10


@pytest.mark.asyncio
async def test_product_model_get_by_brand(register_products):
    prods = await Product.get_by_brand("Testing")
    prods_none = await Product.get_by_brand("Any")

    assert len(prods_none) == 0
    assert len(prods) == 10

@pytest.mark.asyncio
async def test_product_model_count(register_products, user_instance: User):
    user = await user_instance.new()
    counter = await Product.count()
    assert counter == 10

    await Product(
        name=f"Test Product",
        category="Tests2",
        brand="Testing2",
        barcode=f"00000020",
        description="This is a test product",
        pack=2,
        acquisition_price=0.99,
        selling_price=1.99,
        created_by=user
    ).new(0)

    counter2 = await Product.count(Product.brand == "Testing2")
    assert counter2 == 1


@pytest.mark.asyncio
async def test_product_model_get_categories(register_products, user_instance: User):
    user = await user_instance.new()

    await Product(
        name=f"Test Product",
        category="Tests2",
        brand="Testing2",
        barcode=f"00000020",
        description="This is a test product",
        pack=2,
        acquisition_price=0.99,
        selling_price=1.99,
        created_by=user
    ).new(0)

    categories = await Product.get_categories()
    assert "Tests" in categories.keys()
    assert "Tests2" in categories.keys()
    assert categories.get("Tests") == 10
    assert categories.get("Tests2") == 1

    
@pytest.mark.asyncio
async def test_product_model_get_brands(register_products, user_instance: User):
    user = await user_instance.new()

    await Product(
        name=f"Test Product",
        category="Tests2",
        brand="Testing2",
        barcode=f"00000020",
        description="This is a test product",
        pack=2,
        acquisition_price=0.99,
        selling_price=1.99,
        created_by=user
    ).new(0)

    brands = await Product.get_brands()
    assert "Testing" in brands.keys()
    assert "Testing2" in brands.keys()
    assert brands.get("Testing") == 10
    assert brands.get("Testing2") == 1


@pytest.mark.asyncio
async def test_product_model_prefit_margin(restart_database, user_instance: User):
    user = await user_instance.new()
    product = await Product(
        name=f"Test Product",
        category="Tests",
        brand="Testing",
        barcode=f"00000021",
        description="This is a test product",
        pack=2,
        acquisition_price=0.99,
        selling_price=1.99,
        created_by=user
    ).new(0)

    assert product.prefit_margin == 1
    assert float(f"{product.prefit_margin_percent:.2f}") == 0.5
    assert utils.decimal_to_str(product.prefit_margin_percent * 100) == "50,25"