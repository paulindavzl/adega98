import pytest
import pytest_asyncio

from adega98.backend.models import Base
from adega98.backend.models.users_model import User
from adega98.backend.core.application import Application
from adega98.backend.models.products_model import Product


app = Application.get_app()


# reinicia o banco de dados
@pytest_asyncio.fixture
async def restart_database():
    app.init_db("database_test.db")
    async with app.engine.begin() as conn:

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        yield

        await conn.run_sync(Base.metadata.drop_all)


# cria uma instância de User
@pytest_asyncio.fixture
def user_instance():
    return User(
        name="Test User",
        email="test0@test.com",
        whatsapp="98999999999",
        password="test123"
    )


# cria uma instância de Product
@pytest_asyncio.fixture
async def product_instance(user_instance: User):
    user = await user_instance.new()
    return Product(
        name="Test Product",
        category="Testes",
        brand="Testing",
        barcode="0000001",
        description="This is a test product",
        pack=2,
        acquisition_price=0.99,
        selling_price=1.99,
        created_by=user
    )

        