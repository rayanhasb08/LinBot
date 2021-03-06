import asyncio
import random

from discord.ext import commands
import os
import discord

from dotenv import load_dotenv
from help_cog import help_cog
from music_cog import music_cog

load_dotenv()
bot = commands.Bot(command_prefix='-')
bot.remove_command('help')
mot_cache = 'messi'

bot.add_cog(help_cog(bot))
bot.add_cog(music_cog(bot))
bot.run(os.getenv("TOKEN"))
