import aiosqlite

async def init_db():
    async with aiosqlite.connect("./db/db.sql") as conn:
        await conn.execute(
        '''CREATE TABLE IF NOT EXISTS "Task_tb" (
        "id"  INTEGER NOT NULL,
        "score"  INTEGER,
        "Name"  TEXT,
        "isActive"  INTEGER DEFAULT 0,
        "flag"  TEXT,
        "location"  TEXT,
        "time"  TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        )''')
        await conn.execute(
        '''CREATE TABLE IF NOT EXISTS "User_tb" (
        "id"  INTEGER NOT NULL,
        "name"  TEXT NOT NULL,
        "surename"  TEXT NOT NULL,
        "score"  INTEGER DEFAULT 0,
        "current_id_task"  INTEGER,
        "completed_tasks"  TEXT,
        "team"  TEXT,
        PRIMARY KEY("id")
        )''')
        await conn.commit()