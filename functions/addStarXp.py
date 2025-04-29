from functions.checkLevelUp import check_level_up
from functions.addXp import add_xp

async def add_star_xp(message, xp_amount=5):
    user = message.author
    guild_id = message.guild.id
    add_xp(user.id, guild_id, xp_amount)
    await check_level_up(user, message.channel)