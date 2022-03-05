import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.on_ready_message = """ ```Commande -help pour la liste des commandes```"""
        self.help_message = """
```
Pour les grands-mères
    -help - Pour voir les commandes disponibles
    -p <Mots clefs> - Trouve la musique sur Youtube et la fait jouer
    -q - Montre la queue
    -s - Skip la vieille musique (s/o metal)
    -c - Arrête la musique et clear la queue
    -l - Disconnect le bot lol
    -pause - Pause la musique
    -resume - Reprends la musique
```
"""
        self.text_channel_list = []

    # some debug info so that we know the bot has started
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        await self.send_to_all(self.on_ready_message)

    @commands.command(name='help', help='Displays all the available commands')
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)
