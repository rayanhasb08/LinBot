import discord
import random
from discord.ext import commands


# region xd
class message_cog(commands.Bot):
    def __init__(self): super().__init__(command_prefix='-')

    word_list = ['messi', 'ronaldo', 'ibrahimovic', 'mbappe']

    async def on_message(self, message):
        print(self.word_list[random.randrange(0, len(self.word_list))])
# endregion
