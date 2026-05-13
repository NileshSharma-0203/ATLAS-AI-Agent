from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.agent_service import run_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await run_agent(request.message)

        return ChatResponse(
            response=result["response"],
            traces=result["traces"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )