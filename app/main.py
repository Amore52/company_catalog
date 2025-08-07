from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import sys

from .database import init_db
from .api import endpoints

logger = logging.getLogger("app.main")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    Выполняется при старте и завершении.
    """
    logger.info("Инициализация базы данных...")
    init_db()
    logger.info("База данных инициализирована.")
    logger.info("Приложение успешно запущено.")
    yield
    logger.info("Приложение остановлено.")


app = FastAPI(
    title="Company Catalog API",
    description="""
    ### API для справочника организаций, зданий и видов деятельности

    Этот API позволяет:
    - Управлять организациями, зданиями и видами деятельности
    - Искать организации по зданию, деятельности, геолокации и названию
    - Поддерживается древовидная структура деятельности (до 3 уровней)

    Все запросы требуют заголовок:
    ```
    api-key: secret-key-123 (оставил тут для простоты, можно использовать его)
    ```

    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Здания", "description": "CRUD операции с зданиями"},
        {"name": "Организации", "description": "CRUD операции с организациями"},
        {"name": "Деятельность", "description": "Работа с видами деятельности (дерево)"},
        {"name": "Поиск", "description": "Поиск организаций по различным критериям"},
    ],
)

app.include_router(endpoints.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в Company Catalog API. Перейдите на /docs для документации."
    }