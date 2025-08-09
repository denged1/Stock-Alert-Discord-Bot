import os

import discord
from discord.ext import commands
import logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s')


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True # Enable message content intent
# intents = discord.Intents.all() # Alternatively, you can use all intents

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def setup_hook():
    # Load cogs/extensions
    await bot.load_extension("commands.alert_loop")
    await bot.load_extension("commands.basic_commands")
    await bot.load_extension("commands.market_commands")

@bot.event
async def on_ready():
    logging.info(f'Starting bot as {bot.user}')
    # The alert loop is started by the AlertCog when the extension loads.


bot.run(TOKEN)
