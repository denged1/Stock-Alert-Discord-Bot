# Stock Alert Discord Bot
Discord bot to give pre-market notifications on SP biggest movers


Make sure to update yfinance, I had a headache with that.

gainers/losers alert will try to grab pre/post market data at 1m interval with .history(period="1d", interval="1m", prepost=True)['Close'].iloc[-1], but defaults to fast_info._prices_1wk_1h_prepost['Close'].iloc[-1]. This will likely happen if called over weekends, but shouldn't matter since post market is closed anyways