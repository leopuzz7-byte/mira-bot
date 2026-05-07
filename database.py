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


# ─── Статистика ───────────────────────────────────────────────────────────────

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}


async def get_weekly_stats(user_id: int) -> dict:
    from collections import Counter
    from datetime import datetime, timedelta

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT before_emotion, after_emotion, created_at
            FROM diary
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            ORDER BY created_at DESC
        """, (user_id,)) as cur:
            rows = await cur.fetchall()
            entries = [dict(r) for r in rows]

    if not entries:
        return {"empty": True}

    bad_before = [
        e["before_emotion"] for e in entries
        if e["before_emotion"] and e["before_emotion"] != "Всё было хорошо"
    ]
    bad_after = [
        e["after_emotion"] for e in entries
        if e["after_emotion"] and "Хорошо поела" not in e["after_emotion"]
    ]

    top_before = Counter(bad_before).most_common(1)
    top_after  = Counter(bad_after).most_common(1)

    unique_days = len(set(e["created_at"][:10] for e in entries))

    today      = datetime.now()
    week_start = today - timedelta(days=6)

    def fmt_date(d: datetime) -> str:
        return f"{d.day} {MONTHS_RU[d.month]}"

    return {
        "empty":       False,
        "total":       len(entries),
        "days":        unique_days,
        "top_before":  top_before[0] if top_before else None,
        "top_after":   top_after[0]  if top_after  else None,
        "period":      f"{fmt_date(week_start)} — {fmt_date(today)}",
    }


def format_stats_text(stats: dict) -> str:
    if stats.get("empty"):
        return (
            "🌿 Твоя неделя с Мирой\n\n"
            "Пока нет записей за эту неделю.\n"
            "Начни вести дневник, и я покажу твои паттерны 🩵"
        )

    lines = [
        "🌿 Твоя неделя с Мирой",
        stats["period"] + "\n",
        f"Записей в дневнике: {stats['total']}",
        f"Дней с Мирой: {stats['days']} из 7",
    ]

    if stats["top_before"]:
        emotion, count = stats["top_before"]
        times = "раз" if count == 1 else "раза" if count < 5 else "раз"
        lines.append(f"Чаще всего до еды: {emotion.lower()} ({count} {times})")

    if stats["top_after"]:
        emotion, count = stats["top_after"]
        times = "раз" if count == 1 else "раза" if count < 5 else "раз"
        lines.append(f"Чаще всего после еды: {emotion.lower()} ({count} {times})")

    lines.append("\nТы замечаешь себя. Это уже работа 🩵")
    return "\n".join(lines)
