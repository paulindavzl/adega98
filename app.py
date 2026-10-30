import uvicorn
import contextlib

from adega98.backend.core.application import Application


@contextlib.asynccontextmanager
async def lifeaspan(app: Application):
    app.register_routers()

    yield


app = Application.get_app()
app.set_lifespan(lifeaspan)


def run():
    uvicorn.run("app:app")