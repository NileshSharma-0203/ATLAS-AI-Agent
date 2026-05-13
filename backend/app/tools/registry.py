from app.tools.base import BaseTool
from app.tools.terminal import RunShellCommandTool
from app.tools.filesystem import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self):
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools.values()
        ]


tool_registry = ToolRegistry()

tool_registry.register(ListDirectoryTool())
tool_registry.register(ReadFileTool())
tool_registry.register(WriteFileTool())
tool_registry.register(RunShellCommandTool())