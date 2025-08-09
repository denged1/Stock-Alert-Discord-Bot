import pandas_market_calendars as mcal
from datetime import datetime
import pytz

##################  Helper Functions  #################
def log_alert(body: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    new_entry = f"{now} Alert:\n\n{body}\n\n{'-' * 40}\n"

    try:
        with open("alerts_archive.txt", "r") as f:
            existing = f.read()
    except FileNotFoundError:
        existing = ""

    with open("alerts_archive.txt", "w") as f:
        f.write(new_entry + existing)

def is_trading_day():
    """
    Check if today is a trading day (NYSE).
    """
    nyse = mcal.get_calendar('NYSE')
    now = datetime.now(pytz.utc)  # Use UTC for pandas_market_calendars
    today = now.date()
    trading_days = nyse.valid_days(start_date=today, end_date=today)
    return not trading_days.empty

# Formatters
def format_percentage(v):
    try: return f"{float(v)*100:.2f}%"
    except: return "—"

def format_large_num(v):
    try:
        v = float(v)
        if v >= 1e12: return f"{v/1e12:.2f}T"
        if v >= 1e9:  return f"{v/1e9:.2f}B"
        if v >= 1e6:  return f"{v/1e6:.2f}M"
        if v >= 1e3:  return f"{v/1e3:.2f}K"
        return f"{v:.2f}"
    except:
        return "—"
    
def normalize_ticker(t: str) -> str:
    return t.replace('.', '-').upper().strip()