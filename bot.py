import discord
import sqlite3
from discord.ext import commands, tasks
from colorama import *
import random
import time
import requests
import os
import dotenv
import asyncio
import json
# SQL stuff
conn = sqlite3.connect("leveling.db")
cursor = conn.cursor()

# Functions
from functions.addStarXp import add_star_xp
from functions.addXp import add_xp
from functions.removeXp import remove_xp
from functions.checkLevelUp import check_level_up, calculate_xp_for_level
from functions.getMultiplier import get_multiplier
from functions.tags import tagresponder, show_tags

# Views
from commands.helpCommand import HelpView

# Commands
from functions.autoresponder import autoresponder, show_keywords, config

# Loading doetenv
dotenv.load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
bot = commands.Bot(command_prefix="!!", intents=intents, help_command=None)
bot.remove_command('help')
intents.all()
intents.members = True
# Values
SPECIAL_CHANNELS = [1242015121040080917, 1270359419862909020]  # replace with real IDs
BLACKLISTED_CHANNELS = [1352349213614145547]
XP_MULTIPLIER = 1

# Your Discord user ID (replace with your actual ID)
OWNER_ID = 1031798724483096628  # Replace this with your actual Discord ID
COMMANDS_CHANNEL = 1300199215246479443

async def is_command_channel(ctx):
    if ctx.channel.id != COMMANDS_CHANNEL:
        warning_message = await ctx.send("You can only use that command in <#1300199215246479443> "+ctx.author.mention)
        await warning_message.delete(delay=2)
        await ctx.message.delete()
        return False
    else:
        return True


async def is_moderator(ctx):
    # Replace with your actual moderator role ID
    moderator_role_id = 1242051406580416574

    if any(role.id == moderator_role_id for role in ctx.author.roles):
        return True
    warning_message = await ctx.send("You don't have permisions to use this!")
    await warning_message.delete(delay=5)
    await ctx.message.delete()
    return False


async def is_dev(ctx):
    dev_role_id = 1238217978680442980

    if any(role.id == dev_role_id for role in ctx.author.roles):
        return True
    warning_message = await ctx.send("You don't have permisions to use this!")
    await warning_message.delete(delay=5)
    await ctx.message.delete()
    return False

@bot.event
async def on_ready():
    voice_xp_loop.start()
    print(Back.GREEN+"BOT READY | -S-T-A-R-T--B-O-T-"+Style.RESET_ALL)

# Cooldown dictionary to track user message times
message_cooldown = {}
MESSAGE_COOLDOWN_TIME = 5  # Cooldown time in seconds

# Autoresponder and chat xp
@bot.event
async def on_message(message):
    if message.author.bot:  # Ignore bots, including the bot itself
        return

    user_id = message.author.id
    current_time = asyncio.get_event_loop().time()

    # Check if the user is on cooldown
    if user_id in message_cooldown:
        message_count = message_cooldown[user_id]["count"]
        last_message_time = message_cooldown[user_id]["time"]

        if current_time - last_message_time < 3 and message_count >= 10:
            print(f"User {user_id} is on cooldown.")
            return

        if message_count < 10:
            message_cooldown[user_id]["count"] += 1
        else:
            message_cooldown[user_id]["time"] = current_time
    else:
        message_cooldown[user_id] = {"count": 1, "time": current_time}

    if message.content.startswith("!!!"):
        tag_name = message.content[3:].strip()
        await tagresponder(message, override_keyword=tag_name)
    else:
        await bot.process_commands(message)

    await autoresponder(message)

    # XP logic
    base_xp = 4
    multiplier = get_multiplier(message.guild.id)
    xp_gain = int(base_xp * multiplier)
    if message.channel.id in SPECIAL_CHANNELS:
        base_xp += 10

    if not message.content.startswith("!!"):
        add_xp(message.author.id, message.guild.id, xp_gain)
        await check_level_up(message.author, message, message.channel)


# Add xp for stars
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot or user == reaction.message.author:  # Ignore bots and self-reactions
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
                    if not member.bot:  # Ignore bots
                        multiplier = get_multiplier(guild.id)
                        xp_gain = int(1 * multiplier)
                        add_xp(member.id, guild.id, xp_gain)

# ---COMMANDS---
#tags
@bot.command()
async def tags(ctx, *, keyword: str = None):
    await ctx.reply("Use `!!!<keyword>` to use tags")
    await show_tags(ctx)

# yapping
@bot.command()
async def yapping(ctx):
    await ctx.send('Shhhh! Calm down!')

# wordlist
@bot.command()
async def wordlist(ctx):
    await show_keywords(ctx)

# help
@bot.command()
async def help(ctx):
    """Displays the interactive help menu with buttons"""
    view = HelpView()
    await ctx.send(embed=view.embeds[0], view=view)

# issue8ball
@bot.command()
async def issue8ball(ctx):
    responses = ["Will be fixed", "Will be fixed soon", "We will think on the resolution", "We will not fix this", "We don't know how to fix this", "I gotta ask MrSpinn", "Go ask egorro"]
    await ctx.reply(random.choice(responses))

# notifytesters
@bot.command()
async def notifytesters(ctx):
    if not ctx.guild.id == 1232693376646643836:
        await ctx.message.delete()
        response_message = await ctx.send(f"Pls use the dev server, not the public one {ctx.author.mention}")
        await response_message.delete(delay=3)
        return
    with open('././config/testingurl.json', 'r') as f:
        config = json.load(f)
    url = config['url']
    channel = bot.get_channel(1342156641843548182)
    embed=discord.Embed(title="New testing URL", description=f"{url}", color=0xff0000)
    embed.set_thumbnail(url="https://images.cooltext.com/5724188.gif")
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")
    embed.set_footer(text="Open the link and give us ur feedback pls")
    f.close()
    await channel.send(embed=embed)

# newtest
@bot.command()
async def istesting(ctx, status: str):
    channel = bot.get_channel(1341080131841556532)
    if status.lower() == "up":
        embed = discord.Embed(title="Testing site is **up**", description="You can test it", color=0x63EEAA)
        embed.set_footer(text="The URL is inside the testing-link channel")
        await channel.send(embed=embed)
    elif status.lower() == "down":
        embed = discord.Embed(title="Testing site is **down**", description="You can't test it", color=0xFF5151)
        embed.set_footer(text="The URL is inside the testing-link channel")
        await channel.send(embed=embed)
    else:
        response = await ctx.send(f"{ctx.author.mention} Please provide a valid status")
        await ctx.message.delete()
        await response.delete(delay=1)

# testing urls
@bot.command()
async def testingurlset(ctx, new_url: str):
    await is_dev(ctx)
    if not ctx.guild.id == 1232693376646643836:
        warning_message = await ctx.send("Please don't send sensitive data here, I will delete the original message and send you a DM")
        await warning_message.delete(delay=2)
        await ctx.message.delete()
        await ctx.author.send(f"Please don't send sensitive data on the public server, i already deleted the original message")
        return

    if not new_url.startswith("http://") and not new_url.startswith("https://"):
        await ctx.send("Please provide a valid URL starting with http:// or https://")
        return

    try:
        with open('././config/testingurl.json', 'r') as f:
            config = json.load(f)
        
        config["url"] = new_url

        with open('././config/testingurl.json', 'w') as f:
            json.dump(config, f, indent=4)

        await ctx.send(f"The testing URL has been updated to: {new_url}")

    except Exception as e:
        await ctx.send(f"An error occurred while updating the URL: {str(e)}")
    f.close()
@bot.command()
async def testingurlget(ctx):
    if not ctx.guild.id == 1232693376646643836:
        await ctx.message.delete()
        response_message = await ctx.send(f"Nuh uh, u dont have perms {ctx.author.mention}")
        await response_message.delete(delay=3)
        return
    with open('././config/testingurl.json', 'r') as f:
        config = json.load(f)
    await ctx.author.send(f"The current testing URL is: {config['url']}")
    f.close()

# autoreplying dummy
@bot.command()
async def autoreplying(ctx):
    embed = discord.Embed(title="Looks like u got confused!", color=0x71A1F7)
    embed.add_field(name="Ye, definetily, !!autoreplying is not the command u looking for", value="Try typing 'greg' and see the bot reply, and you used it by typing !!autoreplying, you sure you will remember?")
    embed.set_footer(text="if u wont remember this, then take ur dementia pills, dont forget!")
    await ctx.send(embed=embed)

# members
@bot.command()
async def members(ctx):
    embed=discord.Embed(title="How many members on our discord?", color=0xFFD700)
    embed.add_field(name="This many:", value=f"{ctx.guild.member_count}", inline=False)
    await ctx.send(embed=embed)


# Enable autoreply
@bot.command()
async def replyon(ctx):
    if not await is_moderator(ctx):
        return
    config["autoreplying"]["enabled"] = True
    await ctx.message.delete()
    with open('././config/replyingconfig.json', 'w') as f:
        json.dump(config, f)
    response = await ctx.send(f"{ctx.author.mention} enabled autoreplies")
    await response.delete(delay=3)

@bot.command()
async def replyoff(ctx):
    if not await is_moderator(ctx):
        return
    config["autoreplying"]["enabled"] = False
    await ctx.message.delete()
    with open('././config/replyingconfig.json', 'w') as f:
        json.dump(config, f)
    response = await ctx.send(f"{ctx.author.mention} disabled autoreplies")
    await response.delete(delay=3)


# statusbot
@bot.command()
async def statusbot(ctx):
    if await is_command_channel(ctx):
        embed = discord.Embed(title="Blueprint-Bot status", color=0x00CC73)
        embed.add_field(name="Uhhh", value="As u can see i responded, that means im online!")
        await ctx.send(embed=embed)

# socials
@bot.command()
async def socials(ctx):
    embed = discord.Embed(title="Our Socials!", description="check them out", color=0x1DA1F2)
    embed.add_field(name="X (twitter)", value="https://x.com/blueprint_site", inline=False)
    embed.add_field(name="Bluesky", value="https://bsky.app/profile/blueprint-site.bsky.social", inline=False)
    embed.add_field(name="Mastodon", value="https://mastodon.social/@blueprint_site", inline=False)
    await ctx.send(embed=embed)

# status
@bot.command()
async def status(ctx):
    if await is_command_channel(ctx):
        # Domain
        if requests.get("https://blueprint-create.com").status_code == 200:
            production = "Online"
        else:
            production = f"Offline / Not working (Error {requests.get('https://blueprint-create.com').status_code})"
        # API
        if requests.get(os.getenv("PING2")).status_code == 200:
            api = "Online"
        else:
            api = f"Offline / Not working (Error {requests.get('PING2').status_code})"
        # Meilisearch
        if requests.get(os.getenv("PING1")).status_code == 200:
            meilisearch = "Online"
        else:
            meilisearch = f"Offline / Not working (Error {requests.get('PING1').status_code})"
        # Legacy
        if requests.get("https://blueprint-site.github.io/").status_code == 200:
            production_gh = "Online"
        else:
            production_gh = f"Offline / Not working (Error {requests.get('https://blueprint-site.github.io/').status_code})"    
        # Embeds
        embed = discord.Embed(title="The Blueprint Status", color=0x362D52)
        embed.add_field(name="Site (Production)", value=production, inline=False)
        embed.add_field(name="API", value=api, inline=False)
        embed.add_field(name="Meilisearch API", value=meilisearch, inline=False)
        embed.add_field(name="Site (Legacy, Github Pages)", value=production_gh, inline=False)
        embed.add_field(name="Bot", value="If i respond that means im online", inline=False)
        await ctx.send(embed=embed)

# v2 is coming
@bot.command()
async def v2iscoming(ctx):
    if ctx.message.reference:
        ref = ctx.message.reference
        msg = await ctx.channel.fetch_message(ref.message_id)
        await msg.reply("Bro, v2 is coming **SOON**! I promise! (check out snek-peks)")
    else:
        await ctx.send("Bro, v2 is coming **SOON**! I promise! (check out snek-peks)")

# RANKS
# Command to check user's xp
@bot.command()
async def rank(ctx, *, user: discord.Member=None):
    if await is_command_channel(ctx):
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
            print(Back.RED + "Error occurred when fetching user data: " + str(e) + Style.RESET_ALL)

# Command to show top users
@bot.command()
async def top(ctx, num: int = 10):
    """
    Show top users in the server
    """
    if await is_command_channel(ctx):
        # Send a temporary embed while data is being generated
        loading_embed = discord.Embed(
            title="Generating Leaderboard...",
            description="Please wait while I fetch the top users.",
            color=discord.Color.orange()
        )
        loading_message = await ctx.send(embed=loading_embed)

        cursor.execute("SELECT user_id, xp FROM users WHERE guild_id=? ORDER BY xp DESC LIMIT ?", (ctx.guild.id, num))
        data = cursor.fetchall()

        if not data:
            await loading_message.delete()
            await ctx.send("No data found for this server.")
            return

        # Create the final embed for the leaderboard
        leaderboard_embed = discord.Embed(
            title=f"Top {num} Users in {ctx.guild.name}",
            color=discord.Color.blue()
        )

        for i, (user_id, xp) in enumerate(data, start=1):
            try:
                member = ctx.guild.get_member(user_id) or await ctx.guild.fetch_member(user_id)
                name = member.display_name
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                name = f"Unknown User ({user_id})"

            # Calculate level using the algorithm from checkLevelUp.py
            level = 1
            while xp >= calculate_xp_for_level(level + 1):
                level += 1

            leaderboard_embed.add_field(
                name=f"#{i}: {name}",
                value=f"**Level:** {level} | **XP:** {xp}",
                inline=False
            )

        await loading_message.edit(embed=leaderboard_embed)


# Command to remove/clear xp
@bot.command()
async def removexp(ctx, member: discord.Member, amount: int):
    if await is_command_channel(ctx):
        if await is_moderator(ctx):
            remove_xp(member.id, ctx.guild.id, amount)
            await ctx.send(f"Removed {amount} XP from {member.display_name}.")

@bot.command()
async def addxp(ctx, member: discord.Member, amount: int):
    if await is_command_channel(ctx):
        if await is_moderator(ctx):
            add_xp(member.id, ctx.guild.id, amount)
            await ctx.send(f"Added {amount} XP to {member.display_name}.")

# Command to remove/clear xp from all members
@bot.command()
async def removexpall(ctx, amount: int):
    if await is_command_channel(ctx):
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

@bot.command()
async def setmult(ctx, value: float, minutes: int = 0):
    if await is_command_channel(ctx):
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

@bot.command(name="reset_levels")
@commands.has_permissions(administrator=True)
async def reset_levels(ctx):
    if await is_command_channel(ctx):
        """
        Deletes all level data in the current guild after emoji confirmation.
        """
        warning_embed = discord.Embed(
            title="⚠️ WARNING",
            description="This will **permanently delete all level data** for this server.\n\nDo you want to proceed?",
            color=discord.Color.red()
        )
        warning_embed.set_footer(text="Step 1/2")

        confirm_embed = discord.Embed(
            title="❓ Confirm Deletion",
            description="React with ✅ to confirm deletion or ❌ to cancel.",
            color=discord.Color.orange()
        )
        confirm_embed.set_footer(text="Step 2/2")

        # Step 1: Warning
        await ctx.send(embed=warning_embed)

        # Step 2: Confirmation with reactions
        confirm_msg = await ctx.send(embed=confirm_embed)
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == confirm_msg.id
            )

        try:
            # Wait for the reaction to either be ✅ or ❌
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Timeout",
                description="No reaction received. Deletion cancelled.",
                color=discord.Color.dark_grey()
            )
            await confirm_msg.edit(embed=timeout_embed)
            return

        # React to confirm
        if str(reaction.emoji) == "✅":
            cursor.execute("DELETE FROM users WHERE guild_id=?", (ctx.guild.id,))
            conn.commit()
            success_embed = discord.Embed(
                title="✅ Level Data Deleted",
                description="All level data for this server has been deleted.",
                color=discord.Color.green()
            )
            await confirm_msg.edit(embed=success_embed)
        else:
            cancel_embed = discord.Embed(
                title="❌ Deletion Cancelled",
                description="No data was deleted.",
                color=discord.Color.blurple()
            )
            await confirm_msg.edit(embed=cancel_embed)

@bot.command()
async def remove_top_xp(ctx, position: int):
    if await is_command_channel(ctx):
        if not await is_moderator(ctx):
            return

        cursor.execute("SELECT user_id FROM users WHERE guild_id=? ORDER BY xp DESC LIMIT 1 OFFSET ?", (ctx.guild.id, position - 1))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            cursor.execute("DELETE FROM users WHERE user_id=? AND guild_id=?", (user_id, ctx.guild.id))
            conn.commit()
            await ctx.send(f"Removed all XP and deleted data for the user at position {position} in the leaderboard.")
        else:
            await ctx.send(f"No user found at position {position} in the leaderboard.")

@bot.command()
async def recalculatetop(ctx):
    if await is_command_channel(ctx):
        if not await is_moderator(ctx):
            return

        warning_embed = discord.Embed(
            title="⚠️ WARNING",
            description="This will **recalculate all user levels** based on their current XP.\n\nDo you want to proceed?",
            color=discord.Color.red()
        )
        warning_embed.set_footer(text="Step 1/2")

        confirm_embed = discord.Embed(
            title="❓ Confirm Recalculation",
            description="React with ✅ to confirm recalculation or ❌ to cancel.",
            color=discord.Color.orange()
        )
        confirm_embed.set_footer(text="Step 2/2")

        # Step 1: Warning
        await ctx.send(embed=warning_embed)

        # Step 2: Confirmation with reactions
        confirm_msg = await ctx.send(embed=confirm_embed)
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == confirm_msg.id
            )

        try:
            # Wait for the reaction to either be ✅ or ❌
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Timeout",
                description="No reaction received. Recalculation cancelled.",
                color=discord.Color.dark_grey()
            )
            await confirm_msg.edit(embed=timeout_embed)
            return

        # React to confirm
        if str(reaction.emoji) == "✅":
            cursor.execute("SELECT user_id, xp FROM users WHERE guild_id=?", (ctx.guild.id,))
            data = cursor.fetchall()

            for user_id, xp in data:
                level = 1
                while xp >= calculate_xp_for_level(level + 1):
                    level += 1

                cursor.execute("UPDATE users SET level=? WHERE user_id=? AND guild_id=?", (level, user_id, ctx.guild.id))

            conn.commit()
            success_embed = discord.Embed(
                title="✅ Levels Recalculated",
                description="All user levels have been recalculated based on their current XP.",
                color=discord.Color.green()
            )
            await confirm_msg.edit(embed=success_embed)
        else:
            cancel_embed = discord.Embed(
                title="❌ Recalculation Cancelled",
                description="No levels were recalculated.",
                color=discord.Color.blurple()
            )
            await confirm_msg.edit(embed=cancel_embed)

# Running the bot
print(os.getenv('TOKEN'))
try:
    bot.run(os.getenv('TOKEN'))
except Exception as e:
    print(f"Error: {e}")