import asyncio
from datetime import datetime, timedelta
import logging
import pytz
import discord
import io
from discord.ext import commands


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
        mc = self.bot.get_cog("MarketCommands")
        if mc is None:
            logging.error("MarketCommands cog is not loaded; cannot send alert.")
            return

        # 1) Build once
        png_bytes, elapsed = await mc._build_top5_png()
        header = f"**{datetime.now().strftime('%Y-%m-%d')} Pre-Market Movers**"

        # 2) Fan out to channels using fresh wrappers
        with open("channels.txt") as f:
            for line in f:
                guild_id, channel_id = map(int, line.strip().split(","))
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    logging.warning(f"Channel {channel_id} not found.")
                    continue

                logging.info(f"Sending alert to guild {guild_id}, channel {channel_id}")
                file = discord.File(fp=io.BytesIO(png_bytes), filename="premkt_table.png")
                await channel.send(content=f"{header}\n`{elapsed}`", file=file)

        # 3) Optional explicit cleanup (not strictly necessary)
        del png_bytes
async def setup(bot: commands.Bot):
    await bot.add_cog(AlertCog(bot))
