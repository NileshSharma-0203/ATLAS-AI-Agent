from app.services.ollama_service import chat_completion
from app.tools.registry import tool_registry


def preview_output(output: str, limit: int = 500) -> str:
    if len(output) <= limit:
        return output
    return output[:limit] + "...[truncated]"


async def execute_shell(command: str, traces: list):
    tool = tool_registry.get("run_shell_command")
    args = {"command": command}
    result = await tool.run(**args)

    traces.append({
        "step": 1,
        "action": "tool_call",
        "tool_name": "run_shell_command",
        "arguments": args,
        "success": result.success,
        "output_preview": preview_output(result.output or result.error or ""),
        "error": result.error,
    })

    return {
        "response": f"I ran `{command}`.\n\n{result.output or result.error}",
        "traces": traces,
    }


async def run_agent(user_message: str):
    traces = []
    lower_message = user_message.lower().strip()

    if lower_message in ["run pwd", "pwd"]:
        return await execute_shell("pwd", traces)

    if lower_message in ["run ls", "ls"]:
        return await execute_shell("ls", traces)

    if lower_message in ["run python --version", "python --version"]:
        return await execute_shell("python --version", traces)

    if lower_message in ["run python3 --version", "python3 --version"]:
        return await execute_shell("python3 --version", traces)

    if lower_message in ["run npm --version", "npm --version"]:
        return await execute_shell("npm --version", traces)

    if lower_message in ["run git status", "git status"]:
        return await execute_shell("git status", traces)

    if "list" in lower_message and "backend" in lower_message:
        tool = tool_registry.get("list_directory")
        args = {"path": "backend"}
        result = await tool.run(**args)

        traces.append({
            "step": 1,
            "action": "tool_call",
            "tool_name": "list_directory",
            "arguments": args,
            "success": result.success,
            "output_preview": preview_output(result.output),
            "error": result.error,
        })

        return {
            "response": f"I inspected the backend directory.\n\n{result.output}",
            "traces": traces,
        }

    if "read" in lower_message and "backend/app/main.py" in lower_message:
        tool = tool_registry.get("read_file")
        args = {"path": "backend/app/main.py"}
        result = await tool.run(**args)

        traces.append({
            "step": 1,
            "action": "tool_call",
            "tool_name": "read_file",
            "arguments": args,
            "success": result.success,
            "output_preview": preview_output(result.output),
            "error": result.error,
        })

        messages = [
            {
                "role": "system",
                "content": "Summarize the following code accurately. Do not invent details.",
            },
            {
                "role": "user",
                "content": result.output,
            },
        ]

        summary = await chat_completion(messages)

        traces.append({
            "step": 2,
            "action": "llm_summary",
            "tool_name": None,
            "arguments": None,
            "success": True,
            "output_preview": preview_output(summary),
            "error": None,
        })

        return {
            "response": summary,
            "traces": traces,
        }

    response = await chat_completion([
        {
            "role": "system",
            "content": "You are Atlas Agent, a local AI developer assistant.",
        },
        {
            "role": "user",
            "content": user_message,
        },
    ])

    traces.append({
        "step": 1,
        "action": "llm_response",
        "tool_name": None,
        "arguments": None,
        "success": True,
        "output_preview": preview_output(response),
        "error": None,
    })

    return {
        "response": response,
        "traces": traces,
    }