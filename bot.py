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
from functions.checkLevelUp import check_level_up
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

# Autoresponder and chat xp
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
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

# ---COMMANDS---
#tags
@bot.command()
async def tags(ctx, *, keyword: str = None):
    await ctx.reply("Use `!!<keyword>` to use tags")
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
    embed = discord.Embed(title="Blueprint-Bot status", color=0x00CC73)
    embed.add_field(name="Uhhh", value="As u can see i responded, that means im online!")
    await ctx.send(embed=embed)

# Wikis
@bot.command()
async def wiki(ctx):
    await ctx.send("https://wiki.blueprint-create.com/")
@bot.command()
async def plshelp(ctx):
    await ctx.send("https://wiki.blueprint-create.com/")


# github commands
@bot.command()
async def github(ctx):
    embed=discord.Embed(title="Our GitHub url!", description="Here: https://github.com/blueprint-site/blueprint-site.github.io", color=0x282828)
    await ctx.send(embed=embed)
@bot.command()
async def git(ctx):
    embed=discord.Embed(title="Our GitHub url!", description="Here: https://github.com/blueprint-site/blueprint-site.github.io", color=0x282828)
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
    # Domain
    if requests.get("https://blueprint-create.com").status_code == 200:
        production = "Online"
    else:
        production = f"Offline / Not working (Error {requests.get('https://blueprint-create.com').status_code})"
    # API
    if requests.get(os.getenv("PING2")).status_code == 200:
        api = "Online"
    else:
        api = f"Offline / Not working (Error {requests.get(os.getenv('PING2')).status_code})"
    # Meilisearch
    if requests.get(os.getenv("PING1")).status_code == 200:
        meilisearch = "Online"
    else:
        meilisearch = f"Offline / Not working (Error {requests.get(os.getenv('PING1')).status_code})"
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

# RANKS
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
async def top(ctx, num: int = 10):
    """
    Show top users in the server
    """
    cursor.execute("SELECT user_id, xp FROM users WHERE guild_id=? ORDER BY xp DESC LIMIT ?", (ctx.guild.id, num))
    data = cursor.fetchall()

    if data:
        msg = f"**Top {num} users in {ctx.guild.name}**\n"
        for i, (user_id, xp) in enumerate(data, start=1):
            try:
                member = await ctx.guild.fetch_member(user_id)
                name = member.display_name
            except discord.NotFound:
                name = f"Unknown User ({user_id})"
            except discord.Forbidden:
                name = f"Private User ({user_id})"
            except discord.HTTPException:
                name = f"User ID {user_id}"

            level = int(xp ** 0.25)
            msg += f"{i}. {name} | **Level: {level}** | **XP: {xp}**\n"
        await ctx.send(msg)
    else:
        await ctx.send("No data found for this server.")


# Command to remove/clear xp
@bot.command()
async def removexp(ctx, member: discord.Member, amount: int):
    if await is_moderator(ctx):
        remove_xp(member.id, ctx.guild.id, amount)
        await ctx.send(f"Removed {amount} XP from {member.display_name}.")

@bot.command()
async def addxp(ctx, member: discord.Member, amount: int):
    if await is_moderator(ctx):
        add_xp(member.id, ctx.guild.id, amount)
        await ctx.send(f"Added {amount} XP to {member.display_name}.")

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

@bot.command(name="reset_levels")
@commands.has_permissions(administrator=True)
async def reset_levels(ctx):
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


# Running the bot
token = os.getenv('TOKEN')
print(token[:3])
try:
    bot.run(token)
except Exception as e:
    print(f"Error: {e}")