import random
import discord

RESPONSE_MAP = {
    "github": {
        "description": "Sends a GitHub link",
        "responses": [
            {
                "type": "text",
                "value": "https://github.com/blueprint-site/blueprint-create"
            },
            {
                "type": "embed",
                "value": {
                    "title": "Github repo",
                    "description": "Check out our GitHub repository",
                    "color": 0x000000,
                    "url": "https://github.com/blueprint-site/blueprint-create"
                }
            }
        ]
    },
    "issues": {
        "description": "Sends a link to GitHub issues page",
        "responses": [
            {
                "type": "text",
                "value": "https://github.com/blueprint-site/blueprint-create/issues"
            },
            {
                "type": "embed",
                "value": {
                    "title": "Issues tab",
                    "description": "Link to github issues page",
                    "color": discord.Color.red().value,
                    "url": "https://github.com/blueprint-site/blueprint-create/issues"
                }
            }
        ]
    }
}

async def tagresponder(message, override_keyword: str = None):
    content = override_keyword.lower() if override_keyword else message.content.lower()

    for keyword, data in RESPONSE_MAP.items():
        if keyword in content:
            responses = data["responses"]

            # Try to find embed responses first
            embed_responses = [r for r in responses if r["type"] == "embed"]
            if embed_responses:
                response = random.choice(embed_responses)
                await message.reply(embed=discord.Embed.from_dict(response["value"]))
            else:
                response = random.choice(responses)  # fallback to text
                await message.reply(response["value"])
            return
async def show_tags(ctx):
    """Sends an embed with all available keywords."""
    embed = discord.Embed(title="Available Trigger Words", color=discord.Color.blue())
    embed.description = "\n".join(f"• {keyword}: {data['description']}" for keyword, data in RESPONSE_MAP.items())
    await ctx.send(embed=embed)

