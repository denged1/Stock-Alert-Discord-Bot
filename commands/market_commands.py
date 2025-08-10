import time
import pandas as pd
from discord.ext import commands

import commands.helpers.filter_gainers as filter_gainers
import commands.helpers.gainer_multiThread as gainer_mt
import commands.helpers.market_helper as mh

from .helpers.utility import log_alert, format_large_num, format_percentage, normalize_ticker



################ Commands  ################
class MarketCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='eps', help='Returns the EPS of a given ticker for the past five years. Example: `!eps AAPL`')
    async def eps(self, ctx, ticker: str):
        if not ticker:
            await ctx.send("Please provide a ticker symbol. Example: `!eps AAPL`")
            return
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
    @commands.command()
    async def m2(self, ctx, periods: int = 7):
        """Returns the M2 Money Stock data. Monthly, specify the number of periods to return. 7 by default. Example: `!m2 10`"""
        await ctx.send("Fetching M2 Money Stock data...")
        
        df = mh.m2_data(periods) ##########
        if df is not None and not df.empty:
            # Convert DataFrame to string format
            body = df.to_string()
            await ctx.send(f"```txt\n{body}\n```")
        else:
            await ctx.send("Failed to retrieve M2 Money Supply data.")

    @commands.command(name='price_targets', help='Fetches analyst price targets for a given ticker. Example: `!price_targets AAPL`')
    async def price_targets(self, ctx, ticker: str):
        if not ticker:
            await ctx.send("Please provide a ticker symbol. Example: `!price_targets AAPL`")
            return
        ticker = normalize_ticker(ticker)
        await ctx.send(f"Fetching analyst price targets for {ticker}")
        df = mh.get_price_targets(ticker) ##########
        if df is not None:
            await ctx.send(f"```txt\n{df.to_string(index=True)}\n```")
        else:
            await ctx.send("Failed to retrieve analyst price targets.")
    
    @commands.command(name='holders', help='Fetches major holders data for a given ticker. Example: `!holders AAPL`')
    async def holders(self, ctx, ticker: str):
        if not ticker:
            await ctx.send("Please provide a ticker symbol. Example: `!holders AAPL`")
            return
        ticker = normalize_ticker(ticker) 
        await ctx.send(f"Fetching major holders data for {ticker}")
        df = mh.get_major_holders(ticker) ##########
        if df is not None:
            await ctx.send(f"```txt\n{df.to_string(index=True)}\n```")
        else:
            await ctx.send("Failed to retrieve major holders data.")

async def setup(bot: commands.Bot):
    await bot.add_cog(MarketCommands(bot))
