import time
import pandas as pd
from discord.ext import commands

import commands.helpers.filter_gainers as filter_gainers
import commands.helpers.gainer_multiThread as gainer_mt
import commands.helpers.market_helper as mh

from .helpers.utility import log_alert



################ Commands  ################
class MarketCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='eps', help='Returns the EPS of a given ticker for the past five years')
    async def eps(self, ctx, ticker: str):
        await ctx.send(f"Fetching Diluted EPS data for {ticker}")
        df = mh.get_eps(ticker)
        if df is not None:
            await ctx.send(f"```txt\n{df.to_string(index=False)}\n```")
        else:
            await ctx.send("Failed to retrieve EPS data.")

    @commands.command()
    async def top5(self, ctx):
        """Returns the current top 5 movers in the S&P 500."""
        await ctx.send("Fetching current market data...")

        start = time.time()
        #tickers = ["tsla", "aapl", "msft", "googl", "amzn"]  # Example tickers, replace with actual S&P 500 tickers
        tickers = filter_gainers.getsp500()
        # Use asyncio.to_thread to run the blocking function in a separate thread
        #df = await asyncio.to_thread(filter_gainers.getGainers, tickers)
        df = await ctx.bot.loop.run_in_executor(None, gainer_mt.getGainers_mt, tickers)

        #get the first and last five rows
        top_rows = df.head(5)
        bottom_rows = df.tail(5)

        #combine them into a single DataFrame
        combined_rows = pd.concat([top_rows, bottom_rows]).drop_duplicates()

        end = time.time()
        elapsed = (f"Time taken: {(end - start):.2f} seconds.")

        #convert the combined DataFrame to a string without the index, also formatting the columns
        body = combined_rows.to_string(index=False, formatters={
        'Tckr': lambda x: f"{x:<5}",
        'Premkt Chg': lambda x: f"{x:<7}",
        'Mkt Cap': lambda x: f"{x:<7}",
        'Volume': lambda x: f"{x:<7}"
        })

        body += f"\n\n{elapsed}"
        #log alert to csv
        log_alert(body)

        await ctx.send(f"```txt\n{body}\n```")

async def setup(bot: commands.Bot):
    await bot.add_cog(MarketCommands(bot))
