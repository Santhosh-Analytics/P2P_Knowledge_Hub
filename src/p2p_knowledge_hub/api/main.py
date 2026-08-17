from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from p2p_knowledge_hub.exceptions.sqlalchemy_error import DBConnectionError
from p2p_knowledge_hub.api.routes.documents import router as documents_router
from p2p_knowledge_hub.api.routes.query import router as query_router
from p2p_knowledge_hub.core.logger import AppLogger
from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.api.dependencies import pipeline_lifespan

settings = get_settings()
_logger = AppLogger(settings.logs).get_logger(__name__)


app = FastAPI(
    lifespan=lambda app: pipeline_lifespan(app),
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
)


@app.exception_handler(DBConnectionError)
async def db_connection_exception_handler(request: Request, exc: DBConnectionError):
    lines = str(exc).splitlines()
    _logger.error(
        f"[bold red blink]Ingestion failed for document . \n\n{lines}",
        extra={"markup": True},
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Database operation failed", "details": lines[:2]},
    )


app.include_router(documents_router)
app.include_router(query_router)
