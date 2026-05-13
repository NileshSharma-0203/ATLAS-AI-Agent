import asyncio
import os
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

PROJECT_ROOT = Path.cwd().parent


BLOCKED_COMMANDS = [
    "rm -rf /",
    "sudo rm",
    "shutdown",
    "reboot",
    "mkfs",
    ":(){ :|:& };:",
]


def is_dangerous_command(command: str) -> bool:
    normalized = command.lower().strip()

    return any(blocked in normalized for blocked in BLOCKED_COMMANDS)


@router.websocket("/terminal/ws")
async def terminal_ws(websocket: WebSocket):
    await websocket.accept()

    current_directory = PROJECT_ROOT

    try:
        while True:
            command = await websocket.receive_text()

            command = command.strip()

            if not command:
                continue

            if is_dangerous_command(command):
                await websocket.send_json({
                    "type": "error",
                    "content": f"Blocked dangerous command: {command}",
                })

                await websocket.send_json({
                    "type": "done",
                    "exit_code": 1,
                })

                continue

            # HANDLE cd COMMANDS

            if command.startswith("cd"):
                parts = command.split(maxsplit=1)

                if len(parts) == 1:
                    new_directory = PROJECT_ROOT
                else:
                    target = parts[1]

                    if target == "~":
                        new_directory = PROJECT_ROOT
                    else:
                        new_directory = (
                            current_directory / target
                        ).resolve()

                if (
                    new_directory.exists()
                    and new_directory.is_dir()
                ):
                    current_directory = new_directory

                    await websocket.send_json({
                        "type": "stdout",
                        "content": str(current_directory),
                    })

                    await websocket.send_json({
                        "type": "done",
                        "exit_code": 0,
                    })

                else:
                    await websocket.send_json({
                        "type": "stderr",
                        "content": f"No such directory: {target}",
                    })

                    await websocket.send_json({
                        "type": "done",
                        "exit_code": 1,
                    })

                continue

            await websocket.send_json({
                "type": "status",
                "content": (
                    f"Running: {command}"
                ),
            })

            process = await asyncio.create_subprocess_shell(
                command,
                cwd=str(current_directory),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )

            async def stream_output(stream, stream_type):
                while True:
                    line = await stream.readline()

                    if not line:
                        break

                    await websocket.send_json({
                        "type": stream_type,
                        "content": line.decode(
                            errors="replace"
                        ),
                    })

            await asyncio.gather(
                stream_output(
                    process.stdout,
                    "stdout",
                ),
                stream_output(
                    process.stderr,
                    "stderr",
                ),
            )

            exit_code = await process.wait()

            await websocket.send_json({
                "type": "done",
                "exit_code": exit_code,
            })

    except WebSocketDisconnect:
        print(
            "Persistent terminal disconnected"
        )