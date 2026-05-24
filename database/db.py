import aiosqlite
import json
from datetime import datetime, date, timedelta

DB_PATH = "workers.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                full_name TEXT DEFAULT '',
                balance REAL DEFAULT 0.0,
                total_earned REAL DEFAULT 0.0,
                total_workers INTEGER DEFAULT 0,
                farm_level INTEGER DEFAULT 1,
                last_collect TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                daily_streak INTEGER DEFAULT 0,
                last_daily DATE DEFAULT NULL,
                ref_earned REAL DEFAULT 0.0,
                referred_by INTEGER DEFAULT NULL,
                perm_boosts TEXT DEFAULT '[]',
                achievements TEXT DEFAULT '[]',
                language TEXT DEFAULT 'ru',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                worker_type INTEGER,
                bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS temp_boosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                boost_key TEXT,
                multiplier REAL,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                final_amount REAL,
                fee REAL,
                speed TEXT,
                wallet_type TEXT,
                address TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referee_id INTEGER,
                level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


# ─── USER ────────────────────────────────────────────────────────────────────

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            return await cur.fetchone()


async def create_user(user_id: int, username: str, full_name: str, referred_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users 
               (user_id, username, full_name, referred_by, last_collect)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (user_id, username or "", full_name, referred_by)
        )
        await db.commit()


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE users SET {fields} WHERE user_id = ?", values
        )
        await db.commit()


async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT language FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else "ru"


async def set_user_language(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id)
        )
        await db.commit()


async def get_balance(user_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT balance FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return float(row[0]) if row else 0.0


async def update_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        if amount > 0:
            await db.execute(
                "UPDATE users SET total_earned = total_earned + ? WHERE user_id = ?",
                (amount, user_id)
            )
        await db.commit()


# ─── WORKERS ─────────────────────────────────────────────────────────────────

async def add_worker(user_id: int, worker_type: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO workers (user_id, worker_type) VALUES (?, ?)",
            (user_id, worker_type)
        )
        await db.execute(
            "UPDATE users SET total_workers = total_workers + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


async def get_user_workers(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT worker_type, COUNT(*) as cnt 
               FROM workers WHERE user_id = ? 
               GROUP BY worker_type ORDER BY worker_type""",
            (user_id,)
        ) as cur:
            return await cur.fetchall()


async def get_worker_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM workers WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─── FARM ────────────────────────────────────────────────────────────────────

async def update_farm_level(user_id: int, level: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET farm_level = ? WHERE user_id = ?", (level, user_id)
        )
        await db.commit()


# ─── COLLECT ─────────────────────────────────────────────────────────────────

async def get_last_collect(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT last_collect FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def update_last_collect(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_collect = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


# ─── BOOSTS ──────────────────────────────────────────────────────────────────

async def get_active_boosts(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM temp_boosts 
               WHERE user_id = ? AND expires_at > CURRENT_TIMESTAMP""",
            (user_id,)
        ) as cur:
            return await cur.fetchall()


async def add_temp_boost(user_id: int, boost_key: str, multiplier: float, hours: int) -> bool:
    expires = datetime.now() + timedelta(hours=hours)
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT id FROM temp_boosts 
               WHERE user_id = ? AND boost_key = ? AND expires_at > CURRENT_TIMESTAMP""",
            (user_id, boost_key)
        ) as cur:
            existing = await cur.fetchone()
        if existing:
            return False
        await db.execute(
            """INSERT INTO temp_boosts (user_id, boost_key, multiplier, expires_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, boost_key, multiplier, expires)
        )
        await db.commit()
        return True


async def get_perm_boosts(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT perm_boosts FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return json.loads(row[0]) if row else []


async def add_perm_boost(user_id: int, boost_key: str) -> bool:
    boosts = await get_perm_boosts(user_id)
    if boost_key in boosts:
        return False
    boosts.append(boost_key)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET perm_boosts = ? WHERE user_id = ?",
            (json.dumps(boosts), user_id)
        )
        await db.commit()
    return True


# ─── DAILY ───────────────────────────────────────────────────────────────────

async def get_daily_info(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT daily_streak, last_daily FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            return await cur.fetchone()


async def update_daily(user_id: int, streak: int):
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET daily_streak = ?, last_daily = ? WHERE user_id = ?",
            (streak, today, user_id)
        )
        await db.commit()


# ─── REFERRALS ───────────────────────────────────────────────────────────────

async def get_referrals(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND level = 1",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def add_referral(referrer_id: int, referee_id: int, level: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO referrals (referrer_id, referee_id, level) VALUES (?, ?, ?)",
            (referrer_id, referee_id, level)
        )
        await db.commit()


# ─── WITHDRAWALS ─────────────────────────────────────────────────────────────

async def create_withdrawal(
    user_id: int, amount: float, final_amount: float,
    fee: float, speed: str, wallet_type: str, address: str
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO withdrawals 
               (user_id, amount, final_amount, fee, speed, wallet_type, address)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, amount, final_amount, fee, speed, wallet_type, address)
        )
        await db.commit()
        return cur.lastrowid


async def get_withdrawal(withdraw_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM withdrawals WHERE id = ?", (withdraw_id,)
        ) as cur:
            return await cur.fetchone()


async def update_withdrawal_status(withdraw_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE withdrawals SET status = ? WHERE id = ?", (status, withdraw_id)
        )
        await db.commit()


async def get_withdrawn_today(user_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT COALESCE(SUM(amount), 0) FROM withdrawals
               WHERE user_id = ? 
               AND DATE(created_at) = DATE('now') 
               AND status != 'rejected'""",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return float(row[0]) if row else 0.0


# ─── ACHIEVEMENTS ─────────────────────────────────────────────────────────────

async def get_achievements(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT achievements FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return json.loads(row[0]) if row else []


async def add_achievement(user_id: int, ach_key: str) -> bool:
    achs = await get_achievements(user_id)
    if ach_key in achs:
        return False
    achs.append(ach_key)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET achievements = ? WHERE user_id = ?",
            (json.dumps(achs), user_id)
        )
        await db.commit()
    return True


# ─── TOP ──────────────────────────────────────────────────────────────────────

async def get_top_earned(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT full_name, total_earned FROM users ORDER BY total_earned DESC LIMIT ?",
            (limit,)
        ) as cur:
            return await cur.fetchall()


async def get_top_refs(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT u.full_name, COUNT(r.id) as ref_count
               FROM users u
               LEFT JOIN referrals r ON u.user_id = r.referrer_id AND r.level = 1
               GROUP BY u.user_id
               ORDER BY ref_count DESC
               LIMIT ?""",
            (limit,)
        ) as cur:
            return await cur.fetchall()