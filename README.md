# Stock Alert Discord Bot
Discord bot to give pre-market notifications on SP biggest movers 15 minutes before the market opens


If you want the daily alert, make sure to run !setchannel in the channel you want it. Also it runs really slow bc of yfinance api limits. (Like a minute for the !top5 command)

Make sure to update yfinance, I had a headache with that.

gainers/losers alert will try to grab pre/post market data at 1m interval with .history(period="1d", interval="1m", prepost=True)['Close'].iloc[-1], but defaults to fast_info._prices_1wk_1h_prepost['Close'].iloc[-1]. This will likely happen if called over weekends, but shouldn't matter since post market is closed anyways