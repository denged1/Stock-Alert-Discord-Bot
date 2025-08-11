import yfinance as yf
import pandas as pd
from commands.helpers.utility import format_large_num, format_percentage
import pandas_datareader.data as web
import datetime

def get_eps(ticker: str) -> pd.DataFrame:
    """
    Fetch the diluted EPS data for the past five years for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame containing the EPS data or None if retrieval fails.
    """
    try:
        eps_data = yf.Ticker(ticker).quarterly_income_stmt.loc['Diluted EPS'].dropna()
        if eps_data.empty:
            return None
        df = eps_data.reset_index()
        df.columns = ["Date", "Diluted EPS"]
        return df
    except Exception as e:
        print(f"Error fetching EPS data for {ticker}: {e}")
        return None
    
def get_price_targets(ticker: str) -> pd.DataFrame:
    """
    Fetch analyst price targets for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame containing the analyst price targets or None if retrieval fails.
    """
    try:
        price_targets = yf.Ticker(ticker).analyst_price_targets
        #use is None since .analyst_price_targets is a Dict, and Dict doesn't have an empty attribute
        if price_targets is None:
            return None
        # Format the DataFrame as needed
        df = {"Last Price": price_targets['current'],
            "Mean Target": price_targets['mean'],
            "Median Target": price_targets['median'],
            "High Target": price_targets['high'],
            "Low Target": price_targets['low']}
        return pd.DataFrame(df, index=[ticker])
    except Exception as e:
        print(f"Error fetching analyst price targets for {ticker}: {e}")
        return None
    
def get_major_holders(ticker: str) -> pd.DataFrame:
    """
    Fetch major holders data for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame containing the major holders data or None if retrieval fails.
    """
    try:
        major_holders = yf.Ticker(ticker).major_holders
        if major_holders.empty:
            return None
        # the loc method returns a Series, so we access the first element with .iloc[0]
        df = {"Insiders": format_percentage(major_holders.loc['insidersPercentHeld'].iloc[0]),
            "Institutions": format_percentage(major_holders.loc['institutionsPercentHeld'].iloc[0]),
            "# of Institutions": f"{major_holders.loc['institutionsCount'].iloc[0]:.0f}"}
        return pd.DataFrame(df, index=[ticker])
    except Exception as e:
        print(f"Error fetching major holders for {ticker}: {e}")
        return None
    
def m2_data(periods: int) -> pd.DataFrame:
    """
    Fetch M2 Money Stock data from FRED.
    Returns:
        pd.DataFrame: DataFrame containing M2 Money Stock data.
    """

    start = datetime.datetime(2000, 1, 1)
    end = datetime.datetime.today()

    m2 = web.DataReader("M2SL", "fred", start, end) # M2 Money Stock (seasonally adjusted, billions of dollars)
    if m2.empty:
        return pd.DataFrame()
    m2 = m2.rename(columns={"M2SL": "M2 Money Stock"})
    m2['M2 Money Stock'] = m2['M2 Money Stock'].apply(lambda x: format_large_num(x*10**9)) #manually multiply by 10^9 to convert to dollars
    m2.index = m2.index.to_period("M")

    #reverse the DataFrame to have the most recent date at the top
    return m2.iloc[::-1].head(n=periods)

def get_info(ticker: str):
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info

    website = info.get("website", "N/A")
    # Defensive access with .get() to avoid KeyError if missing
    data = {
        "Ticker": ticker,
        "Company Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "Full Time Employees": info.get("fullTimeEmployees", "N/A"),
        "Country": info.get("country", "N/A"),
    }

    df = pd.DataFrame([data])
    return df, website

