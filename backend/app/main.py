from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ws import router as ws_router
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.tools import router as tools_router
from app.api.files import router as files_router
from app.api.edit import router as edit_router
from app.api.terminal import router as terminal_router
from app.services.memory_service import init_memory_db
app = FastAPI(
    title="Atlas Agent",
    description="Local AI runtime and autonomous developer agent",
    version="0.1.0",
)
@app.on_event("startup")
async def startup_event():
    await init_memory_db()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(tools_router, prefix="/api")
app.include_router(ws_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(edit_router, prefix="/api")
app.include_router(terminal_router, prefix="/api")