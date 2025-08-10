# Stock Alert Discord Bot
Discord bot to give pre-market notifications on SP biggest movers 15 minutes before the market opens

Commands:

Market Commands:
!eps [tcker] - Quarterly diluted EPS that contains all non NaN values from yfinance
!m2 [periods] - Monthly M2 Money Supply from present to Jan 1, 2000. Periods specifies how many periods back
!holders [tcker] - Shows percent ownership of equity by insider and institutional investors.
!price_target [tcker] - Shows stat data on analyst price targets for a stock as well as its latest price
!top5 - Returns the top 5 gainers/losers in the SP500, slow and can take upwards of a full minute.


If you want the daily alert, make sure to run !setchannel in the channel you want it. 

Make sure to update yfinance, I had a headache with that.

gainers/losers alert will try to grab pre/post market data at 1m interval with .history(period="1d", interval="1m", prepost=True)['Close'].iloc[-1], but defaults to fast_info._prices_1wk_1h_prepost['Close'].iloc[-1] if that fails. 
This will likely happen if called over weekends, but shouldn't matter since post market is closed anyways