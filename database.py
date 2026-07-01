"""
ᏖᏕᏕ — database layer.
Single SQLite file (tss.db) holds everything: no paid database needed.
All access goes through the Database class attached to bot.db.
"""

import time

import aiosqlite

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    reason TEXT,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS levels (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 0,
    last_xp_at INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS economy (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    balance INTEGER NOT NULL DEFAULT 0,
    last_daily INTEGER NOT NULL DEFAULT 0,
    last_work INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS shop_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS inventory (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id, item_id)
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    guild_id INTEGER,
    remind_at INTEGER NOT NULL,
    message TEXT
);

CREATE TABLE IF NOT EXISTS welcome_config (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel_id INTEGER,
    welcome_message TEXT,
    leave_channel_id INTEGER,
    leave_message TEXT
);

CREATE TABLE IF NOT EXISTS ticket_config (
    guild_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    support_role_id INTEGER,
    log_channel_id INTEGER,
    panel_channel_id INTEGER
);

CREATE TABLE IF NOT EXISTS tickets (
    channel_id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS study_streaks (
    user_id INTEGER PRIMARY KEY,
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    last_checkin INTEGER NOT NULL DEFAULT 0,
    total_sessions INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS afk (
    user_id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    reason TEXT,
    since INTEGER
);
"""


class Database:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    # ---------- generic helpers ----------
    async def execute(self, query: str, params: tuple = ()):
        conn = self.conn
        assert conn is not None
        await conn.execute(query, params)
        await conn.commit()

    async def fetchone(self, query: str, params: tuple = ()):
        conn = self.conn
        assert conn is not None
        cur = await conn.execute(query, params)
        row = await cur.fetchone()
        await cur.close()
        return row

    async def fetchall(self, query: str, params: tuple = ()):
        conn = self.conn
        assert conn is not None
        cur = await conn.execute(query, params)
        rows = await cur.fetchall()
        await cur.close()
        return rows

    # ---------- moderation ----------
    async def add_warning(self, guild_id, user_id, moderator_id, reason):
        await self.execute(
            "INSERT INTO warnings"
            " (guild_id, user_id, moderator_id, reason, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason, int(time.time())),
        )

    async def get_warnings(self, guild_id, user_id):
        return await self.fetchall(
            "SELECT * FROM warnings WHERE guild_id=? AND user_id=? ORDER BY id DESC",
            (guild_id, user_id),
        )

    async def clear_warnings(self, guild_id, user_id):
        await self.execute(
            "DELETE FROM warnings WHERE guild_id=? AND user_id=?", (guild_id, user_id)
        )

    # ---------- leveling ----------
    async def get_level_row(self, guild_id, user_id):
        row = await self.fetchone(
            "SELECT * FROM levels WHERE guild_id=? AND user_id=?", (guild_id, user_id)
        )
        if row is None:
            await self.execute(
                "INSERT INTO levels (guild_id, user_id) VALUES (?, ?)",
                (guild_id, user_id),
            )
            row = await self.fetchone(
                "SELECT * FROM levels WHERE guild_id=? AND user_id=?",
                (guild_id, user_id),
            )
        return row

    async def set_xp_level(self, guild_id, user_id, xp, level, last_xp_at):
        await self.execute(
            """UPDATE levels SET xp=?, level=?, last_xp_at=?
               WHERE guild_id=? AND user_id=?""",
            (xp, level, last_xp_at, guild_id, user_id),
        )

    async def leaderboard(self, guild_id, limit=10):
        return await self.fetchall(
            "SELECT * FROM levels WHERE guild_id=? ORDER BY xp DESC LIMIT ?",
            (guild_id, limit),
        )

    # ---------- economy ----------
    async def get_economy_row(self, guild_id, user_id):
        row = await self.fetchone(
            "SELECT * FROM economy WHERE guild_id=? AND user_id=?", (guild_id, user_id)
        )
        if row is None:
            await self.execute(
                "INSERT INTO economy (guild_id, user_id) VALUES (?, ?)",
                (guild_id, user_id),
            )
            row = await self.fetchone(
                "SELECT * FROM economy WHERE guild_id=? AND user_id=?",
                (guild_id, user_id),
            )
        return row

    async def add_balance(self, guild_id, user_id, amount):
        await self.get_economy_row(guild_id, user_id)
        await self.execute(
            "UPDATE economy SET balance = balance + ? WHERE guild_id=? AND user_id=?",
            (amount, guild_id, user_id),
        )

    async def set_last_daily(self, guild_id, user_id, ts):
        await self.execute(
            "UPDATE economy SET last_daily=? WHERE guild_id=? AND user_id=?",
            (ts, guild_id, user_id),
        )

    async def set_last_work(self, guild_id, user_id, ts):
        await self.execute(
            "UPDATE economy SET last_work=? WHERE guild_id=? AND user_id=?",
            (ts, guild_id, user_id),
        )

    async def econ_leaderboard(self, guild_id, limit=10):
        return await self.fetchall(
            "SELECT * FROM economy WHERE guild_id=? ORDER BY balance DESC LIMIT ?",
            (guild_id, limit),
        )

    # ---------- shop / inventory ----------
    async def add_shop_item(self, guild_id, name, price, description):
        await self.execute(
            "INSERT INTO shop_items"
            " (guild_id, name, price, description)"
            " VALUES (?, ?, ?, ?)",
            (guild_id, name, price, description),
        )

    async def list_shop_items(self, guild_id):
        return await self.fetchall(
            "SELECT * FROM shop_items WHERE guild_id=? ORDER BY price ASC", (guild_id,)
        )

    async def get_shop_item(self, guild_id, item_id):
        return await self.fetchone(
            "SELECT * FROM shop_items WHERE guild_id=? AND id=?", (guild_id, item_id)
        )

    async def remove_shop_item(self, guild_id, item_id):
        await self.execute(
            "DELETE FROM shop_items WHERE guild_id=? AND id=?", (guild_id, item_id)
        )

    async def add_inventory(self, guild_id, user_id, item_id, qty=1):
        row = await self.fetchone(
            "SELECT * FROM inventory WHERE guild_id=? AND user_id=? AND item_id=?",
            (guild_id, user_id, item_id),
        )
        if row is None:
            await self.execute(
                "INSERT INTO inventory"
                " (guild_id, user_id, item_id, quantity)"
                " VALUES (?, ?, ?, ?)",
                (guild_id, user_id, item_id, qty),
            )
        else:
            await self.execute(
                "UPDATE inventory SET quantity = quantity + ?"
                " WHERE guild_id=? AND user_id=? AND item_id=?",
                (qty, guild_id, user_id, item_id),
            )

    async def get_inventory(self, guild_id, user_id):
        return await self.fetchall(
            """SELECT inventory.quantity, shop_items.name,"
            " shop_items.price, shop_items.id"
            " FROM inventory JOIN shop_items"
            " ON inventory.item_id = shop_items.id"
            " WHERE inventory.guild_id=?"
            " AND inventory.user_id=?"
            " AND inventory.quantity > 0""",
            (guild_id, user_id),
        )

    # ---------- reminders ----------
    async def add_reminder(self, user_id, channel_id, guild_id, remind_at, message):
        await self.execute(
            "INSERT INTO reminders"
            " (user_id, channel_id, guild_id, remind_at, message)"
            " VALUES (?, ?, ?, ?, ?)",
            (user_id, channel_id, guild_id, remind_at, message),
        )

    async def due_reminders(self, now_ts):
        return await self.fetchall(
            "SELECT * FROM reminders WHERE remind_at <= ?", (now_ts,)
        )

    async def delete_reminder(self, reminder_id):
        await self.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))

    # ---------- welcome / leave ----------
    async def set_welcome(self, guild_id, channel_id, message):
        row = await self.fetchone(
            "SELECT * FROM welcome_config WHERE guild_id=?", (guild_id,)
        )
        if row is None:
            await self.execute(
                "INSERT INTO welcome_config"
                " (guild_id, welcome_channel_id, welcome_message)"
                " VALUES (?, ?, ?)",
                (guild_id, channel_id, message),
            )
        else:
            await self.execute(
                "UPDATE welcome_config"
                " SET welcome_channel_id=?, welcome_message=?"
                " WHERE guild_id=?",
                (channel_id, message, guild_id),
            )

    async def set_leave(self, guild_id, channel_id, message):
        row = await self.fetchone(
            "SELECT * FROM welcome_config WHERE guild_id=?", (guild_id,)
        )
        if row is None:
            await self.execute(
                "INSERT INTO welcome_config"
                " (guild_id, leave_channel_id, leave_message)"
                " VALUES (?, ?, ?)",
                (guild_id, channel_id, message),
            )
        else:
            await self.execute(
                "UPDATE welcome_config"
                " SET leave_channel_id=?, leave_message=?"
                " WHERE guild_id=?",
                (channel_id, message, guild_id),
            )

    async def get_welcome_config(self, guild_id):
        return await self.fetchone(
            "SELECT * FROM welcome_config WHERE guild_id=?", (guild_id,)
        )

    # ---------- tickets ----------
    async def set_ticket_config(self, guild_id, **kwargs):
        row = await self.fetchone(
            "SELECT * FROM ticket_config WHERE guild_id=?", (guild_id,)
        )
        if row is None:
            await self.execute(
                "INSERT INTO ticket_config (guild_id) VALUES (?)", (guild_id,)
            )
        for key, value in kwargs.items():
            await self.execute(
                f"UPDATE ticket_config SET {key}=? WHERE guild_id=?", (value, guild_id)
            )

    async def get_ticket_config(self, guild_id):
        return await self.fetchone(
            "SELECT * FROM ticket_config WHERE guild_id=?", (guild_id,)
        )

    async def create_ticket(self, channel_id, guild_id, user_id):
        await self.execute(
            "INSERT INTO tickets (channel_id, guild_id, user_id) VALUES (?, ?, ?)",
            (channel_id, guild_id, user_id),
        )

    async def get_ticket(self, channel_id):
        return await self.fetchone(
            "SELECT * FROM tickets WHERE channel_id=?", (channel_id,)
        )

    async def close_ticket(self, channel_id):
        await self.execute(
            "UPDATE tickets SET status='closed' WHERE channel_id=?", (channel_id,)
        )

    # ---------- todos ----------
    async def add_todo(self, user_id, task):
        await self.execute(
            "INSERT INTO todos (user_id, task, created_at) VALUES (?, ?, ?)",
            (user_id, task, int(time.time())),
        )

    async def list_todos(self, user_id):
        return await self.fetchall(
            "SELECT * FROM todos WHERE user_id=? ORDER BY done ASC, id ASC", (user_id,)
        )

    async def complete_todo(self, todo_id, user_id):
        await self.execute(
            "UPDATE todos SET done=1 WHERE id=? AND user_id=?", (todo_id, user_id)
        )

    async def delete_todo(self, todo_id, user_id):
        await self.execute(
            "DELETE FROM todos WHERE id=? AND user_id=?", (todo_id, user_id)
        )

    # ---------- study streaks ----------
    async def get_streak(self, user_id):
        row = await self.fetchone(
            "SELECT * FROM study_streaks WHERE user_id=?", (user_id,)
        )
        if row is None:
            await self.execute(
                "INSERT INTO study_streaks (user_id) VALUES (?)", (user_id,)
            )
            row = await self.fetchone(
                "SELECT * FROM study_streaks WHERE user_id=?", (user_id,)
            )
        return row

    async def update_streak(
        self, user_id, current, longest, last_checkin, total_sessions
    ):
        await self.execute(
            """UPDATE study_streaks SET current_streak=?, longest_streak=?,
               last_checkin=?, total_sessions=? WHERE user_id=?""",
            (current, longest, last_checkin, total_sessions, user_id),
        )

    # ---------- afk ----------
    async def set_afk(self, user_id, guild_id, reason):
        row = await self.fetchone("SELECT * FROM afk WHERE user_id=?", (user_id,))
        if row is None:
            await self.execute(
                "INSERT INTO afk"
                " (user_id, guild_id, reason, since)"
                " VALUES (?, ?, ?, ?)",
                (user_id, guild_id, reason, int(time.time())),
            )
        else:
            await self.execute(
                "UPDATE afk SET guild_id=?, reason=?, since=? WHERE user_id=?",
                (guild_id, reason, int(time.time()), user_id),
            )

    async def get_afk(self, user_id):
        return await self.fetchone("SELECT * FROM afk WHERE user_id=?", (user_id,))

    async def clear_afk(self, user_id):
        await self.execute("DELETE FROM afk WHERE user_id=?", (user_id,))
