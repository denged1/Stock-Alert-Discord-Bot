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

