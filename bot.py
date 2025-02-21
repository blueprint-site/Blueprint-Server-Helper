import discord
import sqlite3
from discord.ext import commands
from colorama import *
import random
import time
import requests
from autoresponder import *

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for message content access

bot = commands.Bot(command_prefix="?b", intents=intents, help_command=None)

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
    print(Back.GREEN+"BOT READY | -S-T-A-R-T--B-O-T-"+Style.RESET_ALL)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await autoresponder(message)
    await bot.process_commands(message)

# ---COMMANDS---
# yapping
@bot.command()
async def yapping(ctx):
    await ctx.send('Shhhh! Calm down!')

# wordlist
@bot.command()
async def wordlist(ctx):
    await show_keywords(ctx)



# help command
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.page = 0
        self.embeds = self.create_help_embeds()

    def create_help_embeds(self):
        """Creates paginated help embeds"""
        embeds = []

        embed1 = discord.Embed(title="Blueprint Bot - Help (1/3)", color=0x71A1F7)
        embed1.add_field(name="What's this?", value="A bot made for Blueprint duh!")
        embed1.add_field(name="General Commands", value="""
                        **?bhelp** - Shows this help message  
                        **?bstatus** - Checks if the website is online  
                        **?bstatusbot** - Checks if the bot is online  
                        **?byapping** - Makes people stop yapping  
                        **?bwordlist** - Shows what words I respond to  
                        **?bwiki** or **?bplshelp** - Sends a link to the help center  
                        **?bmembers** - Shows how many members are in the Discord  
                        **?bsocials** - Prints out our social media links  
                        **?bgithub** or **?bgit** - Sends a link to our GitHub repository  
                        **?bissue8ball** - Guess our resolution for your issue!
        """, inline=False)
        embeds.append(embed1)

        embed2 = discord.Embed(title="Blueprint Bot - Help (2/3)", color=0x71A1F7)
        embed2.add_field(name="Moderator Tools", value="""
                        **?breplyon** - Turns on autoreplying  
                        **?breplyoff** - Turns off autoreplying  
        """, inline=False)
        embed2.add_field(name="Developer Tools", value="""
                        **?btestingurlset <url>** - Sets the testing URL  
                        **?btestingurlget** - Gets the current testing URL (dm)
                        **?bnotifytesters** - I notify the testers inside <#1342156641843548182>
        """, inline=False)
        embeds.append(embed2)

        embed3 = discord.Embed(title="Blueprint Bot - Help (3/3)", color=0x71A1F7)
        embed3.add_field(name="More Info", value="""
        • Use `?b<command>` to interact with the bot.  
        • Have suggestions? Contact the dev team!  
        """, inline=False)
        embeds.append(embed3)

        return embeds

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, disabled=True, custom_id="prev")
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Moves to the previous help page"""
        self.page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Moves to the next help page"""
        self.page += 1
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        """Updates the embed & button states"""
        for child in self.children:
            if child.custom_id == "prev":
                child.disabled = self.page == 0
            if child.custom_id == "next":
                child.disabled = self.page == len(self.embeds) - 1

        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
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
    with open('testingurl.json', 'r') as f:
        config = json.load(f)
    url = config['url']
    channel = bot.get_channel(1342156641843548182)
    embed=discord.Embed(title="New testing URL", description=f"{url}", color=0xff0000)
    embed.set_thumbnail(url="https://images.cooltext.com/5724188.gif")
    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")
    embed.set_footer(text="Open the link and give us ur feedback pls")
    f.close()
    await channel.send(embed=embed)

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
        with open('testingurl.json', 'r') as f:
            config = json.load(f)
        
        config["url"] = new_url

        with open('testingurl.json', 'w') as f:
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
    with open('testingurl.json', 'r') as f:
        config = json.load(f)
    await ctx.author.send(f"The current testing URL is: {config['url']}")
    f.close()

# autoreplying dummy
@bot.command()
async def autoreplying(ctx):
    embed = discord.Embed(title="Looks like u got confused!", color=0x71A1F7)
    embed.add_field(name="Ye, definetily, ?bautoreplying is not the command u looking for", value="Try typing 'greg' and see the bot reply, and you used it by typing ?bautoreplying, you sure you will remember?")
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
    with open('replyingconfig.json', 'w') as f:
        json.dump(config, f)
    await ctx.send(f"{ctx.author.mention} enabled autoreplies")

@bot.command()
async def replyoff(ctx):
    if not await is_moderator(ctx):
        return
    config["autoreplying"]["enabled"] = False
    with open('replyingconfig.json', 'w') as f:
        json.dump(config, f)
    await ctx.send(f"{ctx.author.mention} disabled autoreplies")


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
    if requests.get("https://api.blueprint-create.com").status_code == 200:
        api = "Online"
    else:
        api = f"Offline / Not working (Error {requests.get('https://api.blueprint-create.com').status_code})"
    # Meilisearch
    if requests.get("https://meilisearch.blueprint-create.com").status_code == 200:
        meilisearch = "Online"
    else:
        meilisearch = f"Offline / Not working (Error {requests.get('https://meilisearch.blueprint-create.com').status_code})"
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



# Running
bot.run("MTIzNDA3MDI3ODM4NDkxNDQ4Mw.GvCaHt.uTG-gMuRPi2rg0KVMOjizr02pjJePB6X0WLY1Q")




