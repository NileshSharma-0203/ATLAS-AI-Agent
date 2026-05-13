import asyncio
from typing import Any

from app.tools.base import BaseTool, ToolResult


BLOCKED_COMMANDS = {
    "rm -rf /",
    "shutdown",
    "reboot",
    "mkfs",
}


class RunShellCommandTool(BaseTool):
    name = "run_shell_command"
    description = "Executes a shell command safely."

    async def run(self, **kwargs: Any) -> ToolResult:
        command = kwargs.get("command")

        if not command:
            return ToolResult(
                success=False,
                output="",
                error="Missing command."
            )

        for blocked in BLOCKED_COMMANDS:
            if blocked in command:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Blocked dangerous command: {blocked}"
                )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=20
                )

            except asyncio.TimeoutError:
                process.kill()

                return ToolResult(
                    success=False,
                    output="",
                    error="Command timed out."
                )

            output = stdout.decode().strip()
            error = stderr.decode().strip()

            return ToolResult(
                success=process.returncode == 0,
                output=output,
                error=error if error else None,
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )