import os
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import time
import pandas_market_calendars as mcal
import pytz
import logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s')
import pandas as pd
import filter_gainers
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True # Enable message content intent
# intents = discord.Intents.all() # Alternatively, you can use all intents

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Starting bot as {bot.user}')
    bot.loop.create_task(alert_loop())


#################  Daily Alert Loop   #################

EST = pytz.timezone("US/Eastern")

async def alert_loop():
    while True:
        now = datetime.now(EST)
        target = now.replace(hour=8, minute=50, second=0, microsecond=0)

        if now >= target:
            target += timedelta(days=1)

        # Wait until the next scheduled time
        wait_time = (target - now).total_seconds()
        logging.info(f"[{now}] Sleeping {wait_time / 60:.2f} minutes until next alert...")
        print(f"[{now}] Sleeping {wait_time / 60:.2f} minutes until next alert...")
        await asyncio.sleep(wait_time)

        # Re-check the day after sleep
        if is_trading_day():
            logging.info("It's a trading day. Sending alert")
            await send_alert()
        else:
            logging.info("Market is closed today.")

async def send_alert():
    start = time.time()
    tickers = filter_gainers.getsp500()
    df = await asyncio.to_thread(filter_gainers.getGainers, tickers)

    #get the first and last five rows
    top_rows = df.head(5)
    bottom_rows = df.tail(5)

    #combine them into a single DataFrame
    combined_rows = pd.concat([top_rows, bottom_rows]).drop_duplicates()

    end = time.time()
    elapsed = (f"Time taken: {end - start} seconds.")

    #convert the combined DataFrame to a string without the index, also formatting the columns
    body = combined_rows.to_string(index=False, formatters={
    'Tckr': lambda x: f"{x:<6}",
    'Premkt Chg': lambda x: f"{x:<12}",
    'Mkt Cap': lambda x: f"{x:<10}",
    'Prev Close': lambda x: f"{x:<12}",
    'Last Price': lambda x: f"{x:<12}",
    'Volume': lambda x: f"{x:<12}"
    })

    body += f"\n\n{elapsed}"
    #log alert to csv
    log_alert(body)


    with open("channels.txt") as f:
        for line in f:
            guild_id, channel_id = map(int, line.strip().split(","))
            channel = bot.get_channel(channel_id)
            if channel:
                logging.info(f"Sending alert to guild {guild_id}, channel {channel_id}")
                await channel.send(f"**{datetime.now().strftime('%Y-%m-%d')} Pre-Market Movers**\n```txt\n{body}\n```")


@bot.command()
async def top5(ctx):
    """Returns the current top 5 movers in the S&P 500."""
    await ctx.send("Fetching current market data...")

    start = time.time()
    #tickers = ["tsla", "aapl", "msft", "googl", "amzn"]  # Example tickers, replace with actual S&P 500 tickers
    tickers = filter_gainers.getsp500()
    # Use asyncio.to_thread to run the blocking function in a separate thread
    df = await asyncio.to_thread(filter_gainers.getGainers, tickers)

    #get the first and last five rows
    top_rows = df.head(5)
    bottom_rows = df.tail(5)

    #combine them into a single DataFrame
    combined_rows = pd.concat([top_rows, bottom_rows]).drop_duplicates()

    end = time.time()
    elapsed = (f"Time taken: {end - start} seconds.")

    #convert the combined DataFrame to a string without the index, also formatting the columns
    body = combined_rows.to_string(index=False, formatters={
    'Tckr': lambda x: f"{x:<6}",
    'Premkt Chg': lambda x: f"{x:<12}",
    'Mkt Cap': lambda x: f"{x:<10}",
    'Prev Close': lambda x: f"{x:<12}",
    'Last Price': lambda x: f"{x:<12}",
    'Volume': lambda x: f"{x:<12}"
    })

    body += f"\n\n{elapsed}"
    #log alert to csv
    log_alert(body)

    await ctx.send(f"```txt\n{body}\n```")


##################  Helper Functions  #################
def log_alert(body: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    new_entry = f"{now} Alert:\n\n{body}\n\n{'-' * 40}\n"

    try:
        with open("alerts_archive.txt", "r") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = ""

    with open("alerts_archive.txt", "w") as f:
        f.write(new_entry + existing)

def is_trading_day():
    """
    Check if today is a trading day (NYSE).
    """
    nyse = mcal.get_calendar('NYSE')
    now = datetime.now(pytz.utc)  # Use UTC for pandas_market_calendars
    today = now.date()
    trading_days = nyse.valid_days(start_date=today, end_date=today)
    return not trading_days.empty
















################ Commands  ################
@bot.command(name='hello', help='Replies with a greeting')
async def hello(ctx):
    await ctx.send('Lebron has entered the court')

@bot.command(name='setchannel', help='Sets the current channel for daily alerts')
@commands.has_permissions(administrator=True)
async def setchannel(ctx):
    """Registers the current channel as the one for daily alerts."""
    with open("channels.txt", "a") as f:
        f.write(f"{ctx.guild.id},{ctx.channel.id}\n")
    await ctx.send("This channel has been set for daily alerts!")

@bot.command(name='removechannel', help='Removes the current channel from daily alerts')
@commands.has_permissions(administrator=True)
async def removechannel(ctx):
    """Removes the current channel from the daily alerts list."""
    lines = []
    with open("channels.txt", "r") as f:
        lines = f.readlines()
    with open("channels.txt", "w") as f:
        for line in lines:
            if line.strip() != f"{ctx.guild.id},{ctx.channel.id}":
                f.write(line)
    await ctx.send("This channel has been removed from daily alerts!")


bot.run(TOKEN)