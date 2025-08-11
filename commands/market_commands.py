import time
import pandas as pd
import discord
from discord.ext import commands
import io

import commands.helpers.filter_gainers as filter_gainers
import commands.helpers.gainer_multiThread as gainer_mt
import commands.helpers.market_helper as mh
import commands.helpers.plotting_helper as ph

from .helpers.utility import log_alert, format_large_num, format_percentage, normalize_ticker



################ Commands  ################
class MarketCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='eps', help='Returns the EPS of a given ticker for the past five years. Example: `!eps AAPL`')
    async def eps(self, ctx, ticker: str):
        await ctx.send(f"Fetching Diluted EPS data for {ticker}")
        df = mh.get_eps(ticker)
        if df is not None:
            image_buffer = ph.plot_eps(df, ticker)
            file = discord.File(fp=image_buffer, filename="eps_chart.png")
            await ctx.send(file=file)
        else:
            await ctx.send("Failed to retrieve EPS data.")
        
    # Error handling has to be done like this
    @eps.error
    async def eps_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a ticker symbol. Example: `!eps AAPL`")
        else:
            # Handle other errors or raise
            raise error
        
    async def _build_top5_png(self) -> tuple[bytes, str]:
        """Compute top/bottom-5 table once and return (png_bytes, elapsed_text)."""
        start = time.time()
        tickers = filter_gainers.getsp500()

        # Using non-multithreaded for testing, has less issues with getting ticker info after
        #df = await ctx.bot.loop.run_in_executor(None, filter_gainers.getGainers, tickers)

        # Using multithreaded version for speed
        df = await self.bot.loop.run_in_executor(None, gainer_mt.getGainers_mt, tickers)

        # get the first and last five rows
        top_rows = df.head(5)
        bottom_rows = df.tail(5)
        combined_rows = pd.concat([top_rows, bottom_rows]).drop_duplicates()

        elapsed = f"Time taken: {(time.time() - start):.2f} seconds."
        buf = ph.plot_top5(combined_rows)   # returns BytesIO
        png_bytes = buf.getvalue()
        buf.close()

        log_alert(elapsed)
        return png_bytes, elapsed

    @commands.command()
    async def top5(self, ctx):
        """Returns the current top 5 movers in the S&P 500."""
        await ctx.send("Fetching current market data (this will take a few minutes)...")
        png_bytes, elapsed = await self._build_top5_png()
        file = discord.File(fp=io.BytesIO(png_bytes), filename="premkt_table.png")
        await ctx.send(file=file)



    @commands.command()
    async def m2(self, ctx, periods: int = 7):
        """Returns the M2 Money Stock data. Monthly, specify the number of periods to return. 7 by default. Example: `!m2 10`"""
        await ctx.send("Fetching M2 Money Stock data...")
        
        # proofing for theo
        if periods > 80:
            periods = 80
            await ctx.send("`periods` must be between 1 and 80. Testing with 80...")
        if periods < 1:
            periods = 7
            await ctx.send("`periods` must be between 1 and 80. Testing with 1...")

        df = mh.m2_data(periods) ##########
        if df is not None and not df.empty:
            # Send visualization
            image_buffer = ph.plot_m2(df)
            file = discord.File(fp=image_buffer, filename="m2_chart.png")
            await ctx.send(file=file)
        else:
            await ctx.send("Failed to retrieve M2 Money Supply data.")

    @commands.command(name='price_targets', help='Fetches analyst price targets for a given ticker. Example: `!price_targets AAPL`')
    async def price_targets(self, ctx, ticker: str):
        ticker = normalize_ticker(ticker)
        await ctx.send(f"Fetching analyst price targets for {ticker}")
        df = mh.get_price_targets(ticker) ##########
        if df is not None:
            buffer = ph.plot_price_targets(df)
            file = discord.File(fp=buffer, filename="price_targets.png")
            await ctx.send(file=file)
        else:
            await ctx.send("Failed to retrieve analyst price targets.")

    
    @price_targets.error
    async def price_targets_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a ticker symbol. Example: `!price_targets AAPL`")
        else:
            # Handle other errors or raise
            raise error
    
    @commands.command(name='holders', help='Fetches major holders data for a given ticker. Example: `!holders AAPL`')
    async def holders(self, ctx, ticker: str):
        ticker = normalize_ticker(ticker) 
        await ctx.send(f"Fetching major holders data for {ticker}")
        df = mh.get_major_holders(ticker) ##########
        if df is not None:
            file = ph.plot_holders(df, ticker)
            await ctx.send(file=discord.File(file, filename="major_holders.png"))
        else:
            await ctx.send("Failed to retrieve major holders data.")

    @holders.error
    async def holders_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a ticker symbol. Example: `!holders AAPL`")
        else:
            # Handle other errors or raise
            raise error

    @commands.command(name='info', help='Fetches company information for a given ticker. Example: `!info AAPL`')
    async def info(self, ctx, ticker: str):
        ticker = normalize_ticker(ticker) 
        await ctx.send(f"Fetching company info for {ticker}")
        df, link = mh.get_info(ticker) ##########
        if df is not None:
            file = ph.plot_info(df)
            await ctx.send(file=discord.File(file, filename="info.png"))
            await ctx.send(link)
        else:
            await ctx.send("Failed to retrieve major holders data.")

    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a ticker symbol. Example: `!info AAPL`")
        else:
            # Handle other errors or raise
            raise error
    


async def setup(bot: commands.Bot):
    await bot.add_cog(MarketCommands(bot))
