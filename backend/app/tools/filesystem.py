from pathlib import Path
from typing import Any

from app.tools.base import BaseTool, ToolResult


PROJECT_ROOT = Path.cwd().parent


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "Lists files and folders inside a directory."

    async def run(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path", ".")

        try:
            target_path = (PROJECT_ROOT / path).resolve()

            if not str(target_path).startswith(str(PROJECT_ROOT.resolve())):
                return ToolResult(success=False, output="", error="Access denied.")

            if not target_path.exists():
                return ToolResult(success=False, output="", error="Path does not exist.")

            if not target_path.is_dir():
                return ToolResult(success=False, output="", error="Path is not a directory.")

            items = []
            for item in target_path.iterdir():
                item_type = "directory" if item.is_dir() else "file"
                items.append(f"{item_type}: {item.name}")

            return ToolResult(success=True, output="\n".join(items))

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads the contents of a text file."

    async def run(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")

        if not path:
            return ToolResult(success=False, output="", error="Missing path.")

        try:
            target_path = (PROJECT_ROOT / path).resolve()

            if not str(target_path).startswith(str(PROJECT_ROOT.resolve())):
                return ToolResult(success=False, output="", error="Access denied.")

            if not target_path.exists():
                return ToolResult(success=False, output="", error="File does not exist.")

            if not target_path.is_file():
                return ToolResult(success=False, output="", error="Path is not a file.")

            content = target_path.read_text(encoding="utf-8")

            return ToolResult(success=True, output=content)

        except UnicodeDecodeError:
            return ToolResult(success=False, output="", error="File is not valid UTF-8 text.")

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes content to a text file."

    async def run(self, **kwargs: Any) -> ToolResult:
        path = kwargs.get("path")
        content = kwargs.get("content")

        if not path:
            return ToolResult(success=False, output="", error="Missing path.")

        if content is None:
            return ToolResult(success=False, output="", error="Missing content.")

        try:
            target_path = (PROJECT_ROOT / path).resolve()

            if not str(target_path).startswith(str(PROJECT_ROOT.resolve())):
                return ToolResult(success=False, output="", error="Access denied.")

            target_path.parent.mkdir(parents=True, exist_ok=True)

            target_path.write_text(content, encoding="utf-8")

            return ToolResult(
                success=True,
                output=f"Successfully wrote file: {path}"
            )

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))        