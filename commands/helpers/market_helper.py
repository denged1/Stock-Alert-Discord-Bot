import yfinance as yf
import pandas as pd
from commands.helpers.utility import format_large_num, format_percentage

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
    

