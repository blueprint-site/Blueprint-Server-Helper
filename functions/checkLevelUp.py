import sqlite3
import discord
import math

# Database connection
conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

# Function to calculate XP for each level with exponential growth
def calculate_xp_for_level(level: int, base_xp: int = 20, growth_factor: float = 2):
    """Calculate XP requirement for a given level with exponential growth."""
    return int(base_xp * (growth_factor ** (level - 1)))

# Example: Print XP requirements for levels 1 to 20
for level in range(1, 21):
    xp_for_level = calculate_xp_for_level(level)
    print(f"Level {level} XP required: {xp_for_level}")

# Function to check if the user leveled up
async def check_level_up(user: discord.User, message: discord.Message, channel: discord.TextChannel):
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?", (user.id, channel.guild.id))
    result = cursor.fetchone()
    if result is None:
        return  # User not found
    xp, level = result
    print("xp:", xp)
    print("level:", level)
    # Calculate the next level requirement using the exponential function
    required_xp = calculate_xp_for_level(level + 1)  # Get XP required for next level
    print("Required XP for next level:", required_xp)
    if xp >= required_xp:
        print("NEXT LEVEL")
        # User has enough XP to level up
        new_level = level + 1
        # Update the level in the DB
        cursor.execute("UPDATE users SET level = ? WHERE user_id = ? AND guild_id = ?", (new_level, user.id, channel.guild.id))
        conn.commit()
        await message.channel.send(f"🎉 {user.mention} leveled up to **Level {new_level}**! GG!")
# Example of how the check_level_up function would be used (typically in an on_message or a similar event)
# await check_level_up(user, message, channel)
