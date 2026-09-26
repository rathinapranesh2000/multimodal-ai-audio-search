"""AudioRAG HTTP application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.library import router as library_router
from app.api.routes.search import router as search_router
from app.core.config import get_settings
from app.core.logging import configure_logging, new_trace_id, reset_trace_id, set_trace_id

configure_logging()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="1.0.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def add_trace_id(request: Request, call_next):
        trace_id = request.headers.get("x-trace-id") or new_trace_id()
        token = set_trace_id(trace_id)
        try:
            response = await call_next(request)
        except Exception:
            reset_trace_id(token)
            raise
        reset_trace_id(token)
        response.headers["x-trace-id"] = trace_id
        return response

    application.include_router(health_router)
    application.include_router(ingest_router)
    application.include_router(library_router)
    application.include_router(search_router)
    return application


app = create_app()
