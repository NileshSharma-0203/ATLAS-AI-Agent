from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any


class ToolResult(BaseModel):
    success: bool
    output: str
    error: str | None = None


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, **kwargs: Any) -> ToolResult:
        pass