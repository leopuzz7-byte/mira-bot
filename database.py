"""
Простая SQLite база. Хранит пользователей и записи дневника.
"""
import aiosqlite
import os
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.getenv("DATABASE_PATH", "mira.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                onboarded   INTEGER DEFAULT 0,
                entry_reason TEXT,          -- почему пришёл (из онбординга)
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS diary (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                before_emotion  TEXT,
                after_emotion   TEXT,
                life_context    TEXT,
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()


# ─── Users ────────────────────────────────────────────────────────────────────

async def upsert_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username=excluded.username
        """, (user_id, username or "", first_name or ""))
        await db.commit()


async def get_user(user_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def set_onboarded(user_id: int, reason: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET onboarded=1, entry_reason=? WHERE user_id=?",
            (reason, user_id)
        )
        await db.commit()


async def is_onboarded(user_id: int) -> bool:
    user = await get_user(user_id)
    return bool(user and user["onboarded"])


# ─── Diary ────────────────────────────────────────────────────────────────────

async def save_diary_entry(
    user_id: int,
    before_emotion: str,
    after_emotion: str,
    life_context: str = "",
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO diary (user_id, before_emotion, after_emotion, life_context)
            VALUES (?, ?, ?, ?)
        """, (user_id, before_emotion, after_emotion, life_context))
        await db.commit()


async def get_last_entries(user_id: int, limit: int = 3) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM diary
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
