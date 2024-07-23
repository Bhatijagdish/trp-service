import inspect

import errors
from database.database import initialize_db
from exception_handlers import rocket_exception_handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, RedirectResponse
from profit.connections import session_conn
from routers import database, generator, profit, check_profit, template, chapter, entity, variables, sources, sql_batch

app = FastAPI(
    debug=True,
    title="Rocket API",
    version="1.4",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    default_response_class=ORJSONResponse,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generator.router, prefix="/api", tags=["generator"])
app.include_router(check_profit.router, prefix="/api", tags=["connection"])
app.include_router(profit.router, prefix="/api/templates/{template_id}", tags=["profit"])
app.include_router(template.router, prefix="/api", tags=["Templates"])
app.include_router(chapter.router, prefix="/api", tags=["Chapters"])
app.include_router(entity.router, prefix="/api", tags=["Entities"])
app.include_router(variables.router, prefix="/api", tags=["Variables"])
app.include_router(sources.router, prefix="/api", tags=["Sources"])
app.include_router(database.router, prefix="/api", tags=["database"])
app.include_router(sql_batch.router, prefix="/api", tags=["sql_batch"])

for error in dir(errors):
    error_type = getattr(errors, error)
    if inspect.isclass(error_type) and issubclass(error_type, errors.RocketError):
        app.add_exception_handler(error_type, rocket_exception_handler)


@app.on_event("startup")
async def db_init() -> None:
    await initialize_db()


@app.on_event("shutdown")
async def close_http_session() -> None:
    session = await session_conn()
    await session.close()


@app.get("/api/")
async def redirect_api_to_docs() -> RedirectResponse:
    """**Redirects user to /docs when requesting the root endpoint**"""
    return RedirectResponse("/api/docs", 308)


@app.get("/")
async def redirect_root_to_docs() -> RedirectResponse:
    """**Redirects user to /docs when requesting the root endpoint**"""
    return RedirectResponse("/api/docs", 308)
