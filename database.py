import aiosqlite
import os
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.getenv("DATABASE_PATH", "mira.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id          INTEGER PRIMARY KEY,
                username         TEXT,
                first_name       TEXT,
                onboarded        INTEGER DEFAULT 0,
                entry_reason     TEXT,
                diary_count      INTEGER DEFAULT 0,
                reminder_index   INTEGER DEFAULT 0,
                last_reminded_at TEXT,
                created_at       TEXT DEFAULT (datetime('now'))
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
        # Миграция — добавить колонки если их нет (для старых БД)
        for col, definition in [
            ("diary_count",      "INTEGER DEFAULT 0"),
            ("reminder_index",   "INTEGER DEFAULT 0"),
            ("last_reminded_at", "TEXT"),
        ]:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
            except Exception:
                pass
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
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
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

async def save_diary_entry(user_id: int, before_emotion: str,
                            after_emotion: str, life_context: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO diary (user_id, before_emotion, after_emotion, life_context)
            VALUES (?, ?, ?, ?)
        """, (user_id, before_emotion, after_emotion, life_context))
        await db.execute(
            "UPDATE users SET diary_count = diary_count + 1 WHERE user_id=?",
            (user_id,)
        )
        await db.commit()


async def get_diary_count(user_id: int) -> int:
    user = await get_user(user_id)
    return user["diary_count"] if user else 0


async def get_last_entries(user_id: int, limit: int = 3) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM diary WHERE user_id=?
            ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


# ─── Reminders ────────────────────────────────────────────────────────────────

async def get_all_onboarded_users() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE onboarded=1"
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def update_reminder_sent(user_id: int, next_index: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET reminder_index=?, last_reminded_at=datetime('now')
            WHERE user_id=?
        """, (next_index, user_id))
        await db.commit()
