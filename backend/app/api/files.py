from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

PROJECT_ROOT = Path.cwd().parent


class SaveFileRequest(BaseModel):
    path: str
    content: str


def is_safe_path(path: Path) -> bool:
    return str(path.resolve()).startswith(str(PROJECT_ROOT.resolve()))


@router.get("/files/tree")
async def file_tree(path: str = "."):
    target_path = (PROJECT_ROOT / path).resolve()

    if not is_safe_path(target_path):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path does not exist")

    if not target_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    items = []

    for item in sorted(
        target_path.iterdir(),
        key=lambda p: (p.is_file(), p.name.lower())
    ):
        if item.name in {
            "venv",
            "node_modules",
            ".git",
            "__pycache__"
        }:
            continue

        relative_path = item.relative_to(PROJECT_ROOT)

        items.append({
            "name": item.name,
            "path": str(relative_path),
            "type": "directory" if item.is_dir() else "file",
        })

    return {
        "path": path,
        "items": items,
    }


@router.get("/files/read")
async def read_file(path: str):
    target_path = (PROJECT_ROOT / path).resolve()

    if not is_safe_path(target_path):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    if not target_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    try:
        return {
            "path": path,
            "content": target_path.read_text(encoding="utf-8"),
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File is not valid UTF-8 text"
        )


@router.post("/files/save")
async def save_file(request: SaveFileRequest):
    target_path = (PROJECT_ROOT / request.path).resolve()

    if not is_safe_path(target_path):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    if not target_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    target_path.write_text(
        request.content,
        encoding="utf-8"
    )

    return {
        "success": True,
        "path": request.path,
    }