import discord

# help command
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.page = 0
        self.embeds = self.create_help_embeds()

    def create_help_embeds(self):
        """Creates paginated help embeds"""
        embeds = []

        embed1 = discord.Embed(title="Blueprint Bot - Help (1/5)", color=discord.Color.yellow())
        embed1.add_field(name="What's this?", value="A bot made for Blueprint duh!")
        embed1.add_field(name="General Commands", value="""
                        **!!help** - Shows this help message  
                        **!!status** - Checks if the website is online  
                        **!!statusbot** - Checks if the bot is online  
                        **!!yapping** - Makes people stop yapping  
                        **!!wordlist** - Shows what words I respond to  
                        **!!wiki** or **!!plshelp** - Sends a link to the help center  
                        **!!members** - Shows how many members are in the Discord  
                        **!!socials** - Prints out our social media links  
                        **!!github** or **!!git** - Sends a link to our GitHub repository  
                        **!!issue8ball** - Guess our resolution for your issue!
                        **!!tags** - Shows all tag keywords, and shows how to use them
        """, inline=False)
        embeds.append(embed1)

        embed2 = discord.Embed(title="Blueprint Bot - Help (2/5)", color=discord.Color.brand_red())
        embed2.add_field(name="Moderator Tools", value="""
                        **!!replyon** - Turns on autoreplying  
                        **!!replyoff** - Turns off autoreplying  
        """, inline=False)
        embed2.add_field(name="Developer Tools", value="""
                        **!!testingurlset <url>** - Sets the testing URL  
                        **!!testingurlget** - Gets the current testing URL (dm)
                        **!!notifytesters** - I notify the testers inside <#1342156641843548182>
                        **!!istesting up/down** - Sends a "testing is up/down" message in tester-announcements
        """, inline=False)
        embeds.append(embed2)

        embed3 = discord.Embed(title="Using tags - Help (3/5)", color=discord.Color.blurple())
        embed3.add_field(name="General Commands", value="""
                        **!!tags** - Shows how to use tags and what tags are available
                        **!!<keyword>** - Replace keyword with one of the keywords listed in !!tags  
        """, inline=False)
        embeds.append(embed3)

        embed4 = discord.Embed(title="Blueprint Bot - Help (4/5)", color=discord.Color.purple())
        embed4.add_field(name="XP Stats",
        value=(
                "1. message: **2xp**\n"
                "2. message in special channel: **4xp**\n"
                "3. starring a message: **3xp**\n"
                "4. talking in a voice channel with min. 2 members and not in AFK VC (every minute): **1xp**"
            ),
        inline=False)
        embed4.add_field(name="Commands", value="""
                        **!!rank [user]** - Check user's rank. Leave blank to check your xp. (WARNING: THE USER WILL RECEIVE A PING)
                        **!!top [num]** - Show top users in the server. Leave blank to show top 10.
                        **!!removexp <user> <amount>** - Moderator only, Remove user's xp
                        **!!removexpall <amount>** - Moderator only, Remove xp from all members (basically xp reset)
                        **!!setmult <value> [minutes]** - Mod only. Set XP multiplier temporarily or permanently.
                        **!!reset_levels** - Mod only. Remove ALL data
                        **!!addxp <user> <amount>** - Mod only. Add xp to a user
                        """, inline=False)
        embeds.append(embed4)

        embed5 = discord.Embed(title="Blueprint Bot - Help (5/5)", color=discord.Color.green())
        embed5.add_field(name="More Info", value="""
        • Use `!!<command>` to interact with the bot.  
        • Have suggestions? Contact the dev team!  
        """, inline=False)
        embeds.append(embed5)


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
