import sqlite3

conn = sqlite3.connect("leveling.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    guild_id INTEGER,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, guild_id)
)""")
c.execute("""
CREATE TABLE IF NOT EXISTS settings (
    guild_id INTEGER PRIMARY KEY,
    xp_multiplier REAL DEFAULT 1
)
""")
c.execute("ALTER TABLE settings ADD COLUMN expires_at INTEGER")
conn.commit()