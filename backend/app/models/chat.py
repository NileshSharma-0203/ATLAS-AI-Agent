from pydantic import BaseModel
from typing import Any, Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AgentTrace(BaseModel):
    step: int
    action: str
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    success: bool | None = None
    output_preview: str | None = None
    error: str | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    traces: list[AgentTrace] = []