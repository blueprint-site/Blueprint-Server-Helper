import discord
from discord.ext import commands, tasks
import sqlite3
import os
from colorama import Back, Fore, Style
import asyncio
import time
# Functions
from checkLevelUp import check_level_up
from addXp import add_xp
from addStarXp import add_star_xp
from removeXp import remove_xp
from getMultiplier import get_multiplier

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents)
bot.remove_command('help')

conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

TOKEN = os.getenv("TOKEN")

# Values
SPECIAL_CHANNELS = [1242015121040080917, 1270359419862909020]  # replace with real IDs
BLACKLISTED_CHANNELS = [1352349213614145547]
XP_MULTIPLIER = 1
async def is_moderator(ctx):
    # Replace with your actual moderator role ID
    moderator_role_id = 1242051406580416574

    if any(role.id == moderator_role_id for role in ctx.author.roles):
        return True
    warning_message = await ctx.send("You don't have permisions to use this!")
    await warning_message.delete(delay=5)
    await ctx.message.delete()
    return False


# On ready event when bot starts
@bot.event
async def on_ready():
    voice_xp_loop.start()
    print(f"{Back.GREEN}Logged in as {bot.user}{Style.RESET_ALL}")

# Add xp
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    base_xp = 2
    if message.channel.id in SPECIAL_CHANNELS:
        base_xp += 4

    multiplier = get_multiplier(message.guild.id)
    xp_gain = int(base_xp * multiplier)

    add_xp(message.author.id, message.guild.id, xp_gain)
    await check_level_up(message.author, message.channel)

    await bot.process_commands(message)

# Add xp for stars
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot or user == reaction.message.author:
        return
    
    if str(reaction.emoji) == "⭐":  # star emoji
        message = reaction.message
        if message.author.bot:
            return
        await add_star_xp(message)


# Check voice channel exp
@tasks.loop(minutes=1)
async def voice_xp_loop():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if vc.id not in BLACKLISTED_CHANNELS and len(vc.members) > 1:
                for member in vc.members:
                    if not member.bot:
                            multiplier = get_multiplier(guild.id)
                            xp_gain = int(1 * multiplier)
                            add_xp(member.id, guild.id, xp_gain)



# Bot commands:
# Command to check user's xp
@bot.command()
async def rank(ctx, *, user: discord.Member=None):
    if user is None:
        user = ctx.author

    try:
        cursor.execute("SELECT xp, level FROM users WHERE user_id=? AND guild_id=?", (user.id, ctx.guild.id))
        data = cursor.fetchone()
        if data:
            xp, level = data
            await ctx.send(f"{user.display_name} | Level: **{level}** | XP: **{xp}**")
        else:
            await ctx.send(f"No data found for {user.display_name}.")
    except sqlite3.Error as e:
        print(Back.RED + "Error occured when fetching user data: " + str(e) + Style.RESET_ALL)

# Command to show top users
@bot.command()
async def top(ctx, num=10):
    """
    Show top users in the server
    """
    cursor.execute("SELECT user_id, xp FROM users WHERE guild_id=? ORDER BY xp DESC LIMIT ?", (ctx.guild.id, num))
    data = cursor.fetchall()

    if data:
        msg = f"**Top {num} users in {ctx.guild.name}**\n"
        for i, (user_id, xp) in enumerate(data, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"User ID {user_id}"
            msg += f"{i}. {name} | **Level: {int(xp ** 0.25)}** | **XP: {xp}**\n"
        await ctx.send(msg)
    else:
        await ctx.send("No data found for this server.")

# Command to remove/clear xp
@bot.command()
async def removexp(ctx, member: discord.Member, amount: int):
    if await is_moderator(ctx):
        remove_xp(member.id, ctx.guild.id, amount)
        await ctx.send(f"Removed {amount} XP from {member.display_name}.")

# Command to remove/clear xp from all members
@bot.command()
async def removexpall(ctx, amount: int):
    if await is_moderator(ctx):
        embed = discord.Embed(title="Remove XP from all members", description="Are you sure?", color=discord.Color.red())
        embed.add_field(name="Amount", value=amount, inline=False)
        embed.add_field(name="Confirm", value="React with \U0000274c to confirm", inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("\U0000274c")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "\U0000274c"

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Timed out.")
        else:
            cursor.execute("SELECT user_id FROM users WHERE guild_id=?", (ctx.guild.id,))
            data = cursor.fetchall()
            for user_id, in data:
                remove_xp(user_id, ctx.guild.id, amount)
            await ctx.send(f"Removed {amount} XP from all members in the server.")

# Setting a multiplier
@bot.command()
async def setmult(ctx, value: float, minutes: int = 0):
    if await is_moderator(ctx):
        if value < 0.1:
            await ctx.send("Multiplier must be greater than 0.")
            return

        expires_at = None
        if minutes > 0:
            expires_at = int(time.time()) + (minutes * 60)

        cursor.execute("""
            INSERT INTO settings (guild_id, xp_multiplier, expires_at)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET xp_multiplier=excluded.xp_multiplier, expires_at=excluded.expires_at
        """, (ctx.guild.id, value, expires_at))
        conn.commit()

        if expires_at:
            await ctx.send(f"Set XP multiplier to **{value}x** for {minutes} minutes.")
        else:
            await ctx.send(f"Set XP multiplier to **{value}x** permanently.")


# Help command
@bot.command()
async def help(ctx):
    multiplier = get_multiplier(ctx.guild.id)
    cursor.execute("SELECT expires_at FROM settings WHERE guild_id=?", (ctx.guild.id,))
    exp_result = cursor.fetchone()

    expires_info = ""
    if exp_result and exp_result[0]:
        remaining = int(exp_result[0] - time.time())
        if remaining > 0:
            minutes_left = remaining // 60
            seconds = remaining % 60
            expires_info = f" | Boost ends in {minutes_left}m {seconds}s"

    embed=discord.Embed(title="How to use the commands", color=discord.Color.purple())
    embed.add_field(
    name="XP Stats",
    value=(
        "1. message: **2xp**\n"
        "2. message in special channel: **4xp**\n"
        "3. starring a message: **3xp**\n"
        "4. talking in a voice channel with min. 2 members and not in AFK VC (every minute): **1xp**"
    ),
    inline=False)
    embed.add_field(name="Commands", value="""
                        **!!rank [user]** - Check user's rank. Leave blank to check your xp. (WARNING: THE USER WILL RECEIVE A PING)
                        **!!top [num]** - Show top users in the server. Leave blank to show top 10.
                        **!!removexp <user> <amount>** - Moderator only, Remove user's xp
                        **!!removexpall <amount>** - Moderator only, Remove xp from all members (basically xp reset)
                        **!!setmult <value> [minutes]** - Mod only. Set XP multiplier temporarily or permanently.
                        """, inline=False)
    
    embed.set_footer(text=f"XP Multiplier: {multiplier}x{expires_info}")

    await ctx.send(embed=embed)


bot.run(TOKEN)
