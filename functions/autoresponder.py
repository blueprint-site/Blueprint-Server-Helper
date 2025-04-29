import random
import discord
import json

# Load configuration from config.json

# Dictionary mapping keywords to responses
RESPONSE_MAP = {
    "when v2": ["Probably this month :)", "very very soon!", "also try: when testing", "I PROMISE SOON! I PROMISE!!!!", "*soon since october*"],
    "greg": [
        "Ever considered going outside?",
        "A billion years to craft a door seems reasonable",
    ],
    "how to contribute": ["For now, contributing outside our small developer circle is not possible, sorry!"],
    "bluprint": ["You made a spelling mistake: it's blu**e**print, not bl**up**rint!"],
    "rlcraft": [
        "RLcraft? Sounds like you need to drink some water",
        "Thirst bar was the best addition to Minecraft /i",
    ],
    "chicken butt": ["*Guess what? Chicken Butt!* :rofl:"],
    "gyatt": ["We do not prohibit brainrot but please stop using it :pray:"],
    "gyat": ["We do not prohibit brainrot but please stop using it :pray:"],
    "sigma": ["We do not prohibit brainrot but please stop using it :pray:"],
    "rizz": ["We do not prohibit brainrot but please stop using it :pray:"],
    "fanum tax": ["We do not prohibit brainrot but please stop using it :pray:"],
    "i have a bug": ["Seems like you have a bug! I recommend using <#1270359419862909020> channel!"],
    "absolute cinema": [
        "https://tenor.com/view/me-atrapaste-es-cine-its-cinema-cinema-esto-es-cine-gif-17729711691959966457"
    ],
    "i luv it": [
        "https://tenor.com/view/i-luv-it-psy-lee-byung-hun-play-001-squid-game-gif-17475670124114634359"
    ],
    "gangam": [
        "https://tenor.com/view/gangnam-style-roland-library-of-ruina-black-silence-gif-17296536706784985963"
    ],
    "how to use the bot": ["try ?bhelp"], "how do i use the bot": ["try ?bhelp"],
    "cog": ["","","","","cog <:trollface:1273246408551698516> https://cdn.discordapp.com/attachments/1300199215246479443/1342176557720015013/m2-res_480p-1.mp4?ex=67b8aed3&is=67b75d53&hm=25eb598fd0d496853df18122c59ec823c41fd558a5dd8e243c11a15aab9cd9f6&"],
    "wrench awards": ["how do u know about this, this is a secret"],
    "gimme invite to this discord pls": ["https://discord.gg/join/ZF7bwgatrT"],
    "when testing": ["we are working on it. probably end of week, end of the next week", "fucking soon"],
    "chat dead": ["It`s not dead it is asleep"],
    "how do i test": ['dm egorro for more info'],
    "how to test": ['dm egorro for more info'],
    "going to sleep": ['good night!'],
    "im egorro": ["no u arent"]
}

with open('./config/replyingconfig.json', 'r') as f:
    config = json.load(f)

async def autoresponder(message):
    # Check if autoreplying is enabled in config
    if not config.get("autoreplying", {}).get("enabled", False):
        return
    else:
        content = message.content.lower()

        for keyword, responses in RESPONSE_MAP.items():
            if keyword in content:
                response = random.choice(responses)
                if response:
                    await message.reply(response)
                return 

async def show_keywords(ctx):
    """Sends an embed with all available keywords."""
    embed = discord.Embed(title="Available Trigger Words", color=discord.Color.blue())
    embed.description = "\n".join(f"• {keyword}" for keyword in RESPONSE_MAP.keys())
    autoreply_status = "enabled" if config.get("autoreplying", {}).get("enabled", False) else "disabled"
    embed.add_field(name="Note", value=f"The autoreply status is now: {autoreply_status}", inline=False)
    await ctx.send(embed=embed)

