"""Search route. Guardrail failures return before any model or database call."""

from fastapi import APIRouter, HTTPException

from app.core.logging import current_trace_id, get_logger
from app.retrieval.answer import EmptyQuery, run_search
from app.schemas import SearchRequest, SearchResponse

logger = get_logger(__name__)
router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    try:
        return run_search(body.query, mode=body.mode, trace_id=current_trace_id())
    except EmptyQuery as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("search_failed")
        raise HTTPException(status_code=503, detail="Search is unavailable") from exc
    except Exception as exc:
        logger.exception("search_failed")
        raise HTTPException(status_code=500, detail="Search failed") from exc
