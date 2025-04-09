import sqlite3
import discord
import math

conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

async def check_level_up(user: discord.User, message: discord.message, channel: discord.TextChannel):
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?", (user.id, channel.guild.id))
    result = cursor.fetchone()

    if result is None:
        return  # User not found

    xp, level = result
    new_level = int(0.1 * math.sqrt(xp))

    if new_level > level:
        # Update the level in the DB
        cursor.execute("UPDATE users SET level = ? WHERE user_id = ? AND guild_id = ?", (new_level, user.id, channel.guild.id))
        conn.commit()

        await message.send(f"🎉 {user.mention} leveled up to **Level {new_level}**! GG!")
