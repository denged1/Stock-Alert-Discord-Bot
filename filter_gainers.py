import yfinance as yf
import pandas as pd
import logging
import concurrent.futures
import random
import time
def format_market_cap(value):
    """
    Format the market cap value into a readable form with T, B, or M suffix.

    Args:
        value (float): The market cap value.

    Returns:
        str: Formatted market cap.
    """
    if value >= 1e12:  # Trillions
        return f"{value / 1e12:.2f} T"
    elif value >= 1e9:  # Billions
        return f"{value / 1e9:.2f} B"
    elif value >= 1e6:  # Millions
        return f"{value / 1e6:.2f} M"
    elif value >= 1e3:  # Thousands
        return f"{value / 1e3:.2f} K"
    else:
        return f"{value:.2f}"

def format_percentage(value):
    return f"{value * 100:.2f}%"

def getsp500():
    """
    Get the list of S&P 500 tickers.

    Returns:
        List[str]: List of S&P 500 tickers.
    """
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500['Symbol'].tolist()




def _normalize_symbol(t: str) -> str:
    return t.replace('.', '-').upper().strip()

def download_data(ticker):
    """
    Get current % change (incl pre/post) vs previous RTH close
    and market cap using only fast_info.
    """
    ticker = _normalize_symbol(ticker)
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
        return ticker, pct_change, prev_close, last_price, market_cap, volume
    except Exception as e:
        logging.warning(f"Error processing {ticker}: {e}")
        return ticker, None, None, None, None, None






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
    filtered_data = [(ticker, pct_change, prev_close, last_price, market_cap, volume) for ticker, pct_change, prev_close, last_price, market_cap, volume in filtered_data if market_cap and pct_change and market_cap > min_market_cap]

    #sort the list by premarket change, then reformat the premarket change
    sorted_data = sorted(filtered_data, key=lambda x: x[1], reverse=True)
    sorted_data = [(tckr, format_percentage(pct_change), format_market_cap(market_cap), f"{prev_close:.2f}", f"{last_price:.2f}", format_market_cap(volume)) for tckr, pct_change, prev_close, last_price, market_cap, volume in sorted_data]

    # Convert to DataFrame for better readability
    result_df = pd.DataFrame(sorted_data, columns=['Tckr', 'Premkt Chg', 'Mkt Cap', 'Prev Close', 'Last Price', 'Volume'])

    return result_df


'''

        try:
            # Fetch premarket data
            data = yf.download(ticker, period="1d", prepost=True)
            
            # Calculate premarket change
            premarket_change = (data['Close'].iloc[-1] / data['Open'].iloc[-1] - 1)
            
            # Get market cap information
            market_cap = yf.Ticker(ticker).info['marketCap']

            # Check if market cap meets minimum and add to list if so
            if market_cap > min_market_cap:
                filtered_data.append((ticker, premarket_change, format_market_cap(market_cap)))
            logging.debug(f"{ticker}: {premarket_change}, {format_market_cap(market_cap)}")
        except Exception as e:
            logging.warning(f"Error processing {ticker}: {e}")
'''