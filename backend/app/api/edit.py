from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ollama_service import chat_completion

router = APIRouter()

PROJECT_ROOT = Path.cwd().parent


class EditProposalRequest(BaseModel):
    path: str
    instruction: str


class EditProposalResponse(BaseModel):
    path: str
    original_content: str
    proposed_content: str


def is_safe_path(path: Path) -> bool:
    return str(path.resolve()).startswith(str(PROJECT_ROOT.resolve()))


@router.post("/edit/propose", response_model=EditProposalResponse)
async def propose_edit(request: EditProposalRequest):
    target_path = (PROJECT_ROOT / request.path).resolve()

    if not is_safe_path(target_path):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    if not target_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    try:
        original_content = target_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not valid UTF-8 text")

    messages = [
        {
            "role": "system",
            "content": (
                "You are Atlas Agent, an AI code editor. "
                "Return ONLY the full updated file content. "
                "Do not include markdown fences. "
                "Do not explain your changes."
            ),
        },
        {
            "role": "user",
            "content": f"""
File path:
{request.path}

Instruction:
{request.instruction}

Original file content:
{original_content}
""",
        },
    ]

    proposed_content = await chat_completion(messages)

    return EditProposalResponse(
        path=request.path,
        original_content=original_content,
        proposed_content=proposed_content.strip(),
    )