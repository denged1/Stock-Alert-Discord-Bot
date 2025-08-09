import asyncio
from datetime import datetime, timedelta
import time
import logging
import pytz
import pandas as pd
from discord.ext import commands

import commands.helpers.filter_gainers as filter_gainers
import commands.helpers.gainer_multiThread as gainer_mt  # available if you want to switch later

from .helpers.utility import log_alert, is_trading_day

#################  Daily Alert Loop   #################

EST = pytz.timezone("US/Eastern")

class AlertCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._task = None

    async def cog_load(self):
        # Start the background loop when the cog is loaded
        self._task = asyncio.create_task(self.alert_loop())

    '''
    async def cog_unload(self):
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task'''

    async def alert_loop(self):
        while True:
            now = datetime.now(EST)
            target = now.replace(hour=8, minute=45, second=0, microsecond=0)

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
                await self.send_alert()
            else:
                logging.info("Market is closed today.")

    async def send_alert(self):
        start = time.time()
        tickers = filter_gainers.getsp500()
        # If you prefer multithreaded version, switch to gainer_mt.getGainers_mt
        #df = await asyncio.to_thread(filter_gainers.getGainers, tickers)
        df = await asyncio.to_thread(gainer_mt.getGainers_mt, tickers)

        #get the first and last five rows
        top_rows = df.head(5)
        bottom_rows = df.tail(5)

        #combine them into a single DataFrame
        combined_rows = pd.concat([top_rows, bottom_rows]).drop_duplicates()

        end = time.time()
        elapsed = (f"Time taken: {(end - start):.2f} seconds.")

        #convert the combined DataFrame to a string without the index, also formatting the columns
        body = combined_rows.to_string(index=False, formatters={
        'Tckr': lambda x: f"{x:<6}",
        'Premkt Chg': lambda x: f"{x:<7}",
        'Mkt Cap': lambda x: f"{x:<7}",
        'Volume': lambda x: f"{x:<7}"
        })

        body += f"\n\n{elapsed}"
        #log alert to csv
        log_alert(body)

        with open("channels.txt") as f:
            for line in f:
                guild_id, channel_id = map(int, line.strip().split(","))
                channel = self.bot.get_channel(channel_id)
                if channel:
                    logging.info(f"Sending alert to guild {guild_id}, channel {channel_id}")
                    await channel.send(f"**{datetime.now().strftime('%Y-%m-%d')} Pre-Market Movers**\n```txt\n{body}\n```")


async def setup(bot: commands.Bot):
    await bot.add_cog(AlertCog(bot))
