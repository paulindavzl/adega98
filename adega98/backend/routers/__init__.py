import fastapi

from ..core.application import Application
from ..core.constants import (
    JS_PATH,
    CSS_PATH,
    FONTS_PATH,
    IMAGES_PATH,
    TEMPLATES_PATH,
)


app = Application.get_app()

# monta rotas estáticas
app.mount(
    js=JS_PATH,
    css=CSS_PATH,
    fonts=FONTS_PATH,
    images=IMAGES_PATH,
    templates=TEMPLATES_PATH
)

# cria a página fixa do sistema
@app.get("/")
async def index(r: fastapi.Request):
    return app.render(r, "index.html")