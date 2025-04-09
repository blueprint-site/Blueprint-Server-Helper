import sqlite3

conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

# Command for adding xp for a user
def add_xp(user_id, guild_id, amount):
    cursor.execute("SELECT xp, level FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    data = cursor.fetchone()
    if data:
        xp, level = data
        xp += amount
        new_level = int(xp ** 0.25)
        if new_level > level:
            cursor.execute("UPDATE users SET xp=?, level=? WHERE user_id=? AND guild_id=?", (xp, new_level, user_id, guild_id))
        else:
            cursor.execute("UPDATE users SET xp=? WHERE user_id=? AND guild_id=?", (xp, user_id, guild_id))
    else:
        cursor.execute("INSERT INTO users (user_id, guild_id, xp, level) VALUES (?, ?, ?, ?)", (user_id, guild_id, amount, 1))
    conn.commit()
