import sqlite3
import time

conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

def get_multiplier(guild_id):
    cursor.execute("SELECT xp_multiplier, expires_at FROM settings WHERE guild_id=?", (guild_id,))
    result = cursor.fetchone()

    if result:
        xp_multiplier, expires_at = result
        if expires_at and expires_at < int(time.time()):
            # Expired – reset to default
            cursor.execute("UPDATE settings SET xp_multiplier=1, expires_at=NULL WHERE guild_id=?", (guild_id,))
            conn.commit()
            return 1
        return xp_multiplier
    return 1
