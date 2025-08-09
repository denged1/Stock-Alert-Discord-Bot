import yfinance as yf
import pandas as pd
import logging
from commands.helpers.utility import format_percentage, format_large_num, normalize_ticker

def getsp500():
    """
    Get the list of S&P 500 tickers.

    Returns:
        List[str]: List of S&P 500 tickers.
    """
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500['Symbol'].tolist()





def download_data(ticker):
    """
    Get current % change (incl pre/post) vs previous RTH close
    and market cap using only fast_info.
    """
    ticker = normalize_ticker(ticker)
    try:
        ti = yf.Ticker(ticker)
        fi = ti.fast_info

        #get the last price INCLUDING pre/post market
        last_price = ti.history(period="1d", interval="1m", prepost=True)['Close'].iloc[-1]
        prev_close = fi.previous_close
        market_cap = fi.market_cap
        volume = fi.last_volume

        if last_price is None or prev_close is None:
            raise ValueError(f"Missing price data for {ticker}")
        
        #if last price doesn't work default to lower resolution pre/post market data-- thinking of weekend in particular
        if prev_close is not None and last_price is None:
            last_price = fi._prices_1wk_1h_prepost['Close'].iloc[-1]

        pct_change = (last_price / prev_close) - 1
        return ticker, pct_change, market_cap, volume
    except Exception as e:
        logging.warning(f"Error processing {ticker}: {e}")
        return ticker, None, None, None






def getGainers(tickers: list[str], min_market_cap=1e9):
    """
    Get the top premarket gainers with a market cap above a specified minimum.

    Args:
        tickers (List[str]): List of tickers to check.
        min_market_cap (float): Minimum market capitalization. Defaults to 1 billion.

    Returns:
        pandas.DataFrame: DataFrame of top premarket gainers.
    """    
    filtered_data = []

    for ticker in tickers:
        filtered_data.append(download_data(ticker))
    #filter results and prepare for DataFrame
    filtered_data = [(ticker, pct_change, market_cap, volume) for ticker, pct_change, market_cap, volume in filtered_data if market_cap and pct_change and market_cap > min_market_cap]

    #sort the list by premarket change, then reformat the premarket change
    sorted_data = sorted(filtered_data, key=lambda x: x[1], reverse=True)
    sorted_data = [(tckr, format_percentage(pct_change), format_large_num(market_cap), format_large_num(volume)) for tckr, pct_change, market_cap, volume in sorted_data]

    # Convert to DataFrame for better readability
    result_df = pd.DataFrame(sorted_data, columns=['Tckr', 'Premkt Chg', 'Mkt Cap', 'Volume'])

    return result_df

