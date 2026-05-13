from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from app.tools.registry import tool_registry

router = APIRouter()


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = {}


@router.get("/tools")
async def list_tools():
    return {
        "tools": tool_registry.list_tools()
    }


@router.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    tool = tool_registry.get(request.tool_name)

    if tool is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tool not found: {request.tool_name}"
        )

    result = await tool.run(**request.arguments)

    return result