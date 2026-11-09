from __future__ import annotations

import fastapi
import fastapi.templating
import fastapi.staticfiles
import starlette.templating
from contextlib import _AsyncGeneratorContextManager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .env import Env
from .logger import Logger


env = Env.get_env()
logger = Logger(__name__)


# classe que engloba aplicação e banco de dados
class Application(fastapi.FastAPI):
    instance: None|Application = None
    
    def __init__(self):
        self.inited = False
        self.routers: dict[str, fastapi.APIRouter] = {}
        self.templates = self.mount(templates="/templates")
        super().__init__()
        logger.info("application started")


    # inicia o banco de dados
    def init_db(self, db_name: str):
        db_url = env.database_url + db_name
        self.engine = create_async_engine(db_url)
        self.session_local = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info("database started")


    def set_lifespan(self, lifespan: None|_AsyncGeneratorContextManager=None):
        self.router.lifespan_context = lifespan
        logger.info("lifespan defined")
        

    # renderiza um template
    def render(self, request: fastapi.Request, filename: str, context: None|dict=None, code=200) -> starlette.templating._TemplateResponse:
        return self.templates.TemplateResponse(
            request=request,
            name=filename,
            context=context,
            status_code=code
        )
        
    
    # monta rota personalizados para arquivos estáticos
    def mount(self, **kw):
        for name, path in kw.items():
            if name == "templates":
                self.templates = fastapi.templating.Jinja2Templates(directory=path)
                return
                
            super().mount(
                f"/{name}",
                fastapi.staticfiles.StaticFiles(directory=path),
                name=name
            )

            logger.info(f"static route mounted in /{name} for {path}")


    # obtém uma rota
    def get_router(self, prefix: str, depends: None|list[fastapi.Depends]=None) -> fastapi.APIRouter:
        router = self.routers.get(prefix)
        if router is None:
            router = fastapi.APIRouter(prefix=f"/{prefix}", dependencies=depends)
            self.routers[prefix] = router

        return router
    

    # registra uma rota
    def register_routers(self):
        for name, router in self.routers.items():
            self.include_router(router)

            logger.info(f"/{name} route registered")
    
    
    @classmethod # obtém a versão global da aplicação
    def get_app(cls) -> Application:
        app = cls.instance
        if app is None:
            app = Application()
            cls.instance = app
            
        return app