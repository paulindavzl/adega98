from __future__ import annotations

import os
import dotenv

from .logger import Logger
from .exceptions import EnvError
from .constants import (
    MISSING_ENV,
    ENVFILE_PATH,
    ENVFILE_NOT_FOUND
)


logger = Logger(__name__)


# classe que gerencia todas as variáveis de ambiente
class Env:
    _instance: None|Env = None 

    database_url: str

    def __init__(self):
        logger.info("env manager started")
        self.load_env()


    # carrega e valida todas as variáveis de ambiente
    def load_env(self):
        if not os.path.exists(ENVFILE_PATH): # verifica se o arquivo existe
            logger.critical(f"envfile not found ({ENVFILE_PATH})")
            raise EnvError(
                cause="envfile_not_found",
                message=ENVFILE_NOT_FOUND
            )
        
        dotenv.load_dotenv(ENVFILE_PATH) # carrega o arquivo
        logger.info("envfile loaded")

        # carrega as variáveis de ambiente pré-definidas
        for name in self.__annotations__.keys():
            if name.startswith("_"): continue

            value = os.getenv(name.upper())
            if value is None: # garante que a variável existe
                logger.critical(f"env variable not found ({name.upper()})")
                raise EnvError(
                    cause="missing_env",
                    message=MISSING_ENV,
                    content={
                        "env_name": name.upper()
                    }
                )
            setattr(self, name, value)

    @classmethod
    def get_env(cls) -> Env:
        instance = cls._instance
        if instance is None:
            instance = Env()
            cls._intance = instance
        
        return instance