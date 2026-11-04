import uvicorn
import contextlib

from adega98.backend.models import Base
from adega98.backend.models.users_model import User
from adega98.backend.core.application import Application


app = Application.get_app()


async def create_user():
    user = User(
        name="TestUser",
        email="test_user@test.com",
        whatsapp="98999999999",
        password="testing123"
    )
    user = await user.new()


@contextlib.asynccontextmanager
async def lifeaspan(app: Application):
    app.register_routers()
    app.init_db("database_test.db")

    async with app.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        await create_user()

    yield

    async with app.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


app.set_lifespan(lifeaspan)


def run():
    uvicorn.run("dev_app:app", reload=True)