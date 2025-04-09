import sqlite3

conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

def remove_xp(user_id, guild_id, amount):
    cursor.execute("SELECT xp, level FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    data = cursor.fetchone()
    if data:
        xp, level = data
        xp = max(0, xp - amount)
        new_level = int(xp ** 0.25)
        cursor.execute("UPDATE users SET xp=?, level=? WHERE user_id=? AND guild_id=?", (xp, new_level, user_id, guild_id))
        conn.commit()