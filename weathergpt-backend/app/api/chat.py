from fastapi import APIRouter, HTTPException

from app.agent.graph import run_agent
from app.models.schemas import ChatRequest, ChatResponse
from app.tools.geocoding import GeocodingError

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # Note: routing itself never raises here - agent/router.py falls back to
    # a rule-based router internally if Groq is unreachable, so the only
    # error we still need to handle at this layer is an unresolvable location.
    try:
        return await run_agent(
            message=request.message,
            location_hint=request.location,
            language=request.language,
        )
    except GeocodingError as e:
        raise HTTPException(status_code=404, detail=str(e))
