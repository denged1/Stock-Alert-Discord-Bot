# Stock Alert Discord Bot
Discord bot to give pre-market notifications on SP biggest movers 15 minutes before the market opens

Set up:
- add a .env file into the same directory as main.py, add the line: DISCORD_TOKEN = {token}
- install packages (Make sure to update yfinance, I had a headache with that.)
- run main.py


Folder structure:
- All async commands and alert loop code is in the /commands/ folder, which act mainly as wrapper functions for files in commands/helpers/. 
- bulk of code logic is in commands/helpers/
    - utility.py -- common helpful functions like formatting pcts and checking if trading day
    - market_helper -- helper functions for market_commands.py, ALL functions return pd.dataframes
    - filter_gainers.py and gainer_multiThread.py both sort through sp500 for gainers/losers. The former is multithreaded and faster, but may run into yfinance rate limits. Both files do the exact same thing, except one is single threaded and one is multithreaded.



Commands:

Market Commands:
- !eps [tcker] - Quarterly diluted EPS that contains all non NaN values from yfinance
- !m2 [periods] - Monthly M2 Money Supply from present to Jan 1, 2000. Periods specifies how many periods back
- !holders [tcker] - Shows percent ownership of equity by insider and institutional investors.
- !price_target [tcker] - Shows stat data on analyst price targets for a stock as well as its latest price
- !top5 - Returns the top 5 gainers/losers in the SP500, slow and can take upwards of a full minute.


If you want the daily alert, make sure to run !setchannel in the channel you want it. 



Future ideas
- adding a debug or testing mode.
- adding plots for stock prices
- setting alerts for specific finviz filter urls
- adding crypto data or alerts

Specific Command ideas
- !news [tcker] -- parses and returns headlines from yf.Ticker(ticker).news for a given stock
- !info [tcker] -- gives basic information like name, sector, employees, market cap, etc.



Current data sources
- yfinance
- fred


Notes:

gainers/losers alert will try to grab pre/post market data at 1m interval with .history(period="1d", interval="1m", prepost=True)['Close'].iloc[-1], but defaults to fast_info._prices_1wk_1h_prepost['Close'].iloc[-1] if that fails. 
This will likely happen if called over weekends, but shouldn't matter since post market is closed anyways