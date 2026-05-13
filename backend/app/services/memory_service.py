import aiosqlite
from datetime import datetime
from pathlib import Path

DB_PATH = Path("atlas_memory.db")


async def init_memory_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS terminal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                output TEXT,
                exit_code INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                instruction TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        await db.commit()


async def save_chat_message(role: str, content: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO chat_history (role, content, created_at)
            VALUES (?, ?, ?)
            """,
            (role, content, datetime.utcnow().isoformat()),
        )

        await db.commit()


async def save_terminal_command(command: str, output: str, exit_code: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO terminal_history (command, output, exit_code, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (command, output, exit_code, datetime.utcnow().isoformat()),
        )

        await db.commit()


async def save_edit_history(file_path: str, instruction: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO edit_history (file_path, instruction, created_at)
            VALUES (?, ?, ?)
            """,
            (file_path, instruction, datetime.utcnow().isoformat()),
        )

        await db.commit()