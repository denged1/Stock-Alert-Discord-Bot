import io
import re
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd


def truncate_text(text, max_chars=20):
    """Truncate text to max_chars adding ellipsis if needed."""
    text = str(text)
    if len(text) > max_chars:
        return text[:max_chars-3] + "..."
    return text


def plot_eps(df, ticker):
    """
    Takes in df with columns ['Date', 'Diluted EPS'] and ticker
    """

    # Set to dates
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])  
    df = df.sort_values('Date')             

    fig, ax = plt.subplots(figsize=(5, 4))

    # Plot EPS over time
    ax.plot(df['Date'], df['Diluted EPS'], marker='o', linewidth=2, color='#4e79a7')

    # Add value labels above points
    for x, y in zip(df['Date'], df['Diluted EPS']):
        ax.text(x, y + 0.05, f"{y:.2f}", ha='center', fontsize=8)

    # Titles/labels/formatting
    ax.set_title(f"Diluted EPS Over Time — {ticker}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Diluted EPS", fontsize=10)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.6)
    y_min = df['Diluted EPS'].min()
    y_max = df['Diluted EPS'].max()
    padding = (y_max - y_min) * 0.15  
    ax.set_ylim(y_min - padding, y_max + padding)
    plt.tight_layout()

    # Send visualization over as buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)

    return buf

# Get rid of extra content from names like Inc. and Corporation
def clean_name(name):
    if not name:
        return "N/A"
    cleaned = re.sub(r",?\s*(Inc\.?|Incorporated|Corp\.?|Corporation)\b\.?", "", name, flags=re.IGNORECASE)
    return cleaned.strip()


# Plotting method for top5
def plot_top5(df):
    """
    Takes in df with columns ['Tckr', 'Premkt Chg', 'Mkt Cap', 'Volume']
    """

    df = df.copy()

    # Rename columns
    rename_map = {
        'Tckr': 'Stock',
        'Mkt Cap': 'Market Cap'
    }
    df.rename(columns=rename_map, inplace=True)

    # extract tickers and add ticker info
    tickers = df['Stock'].str.extract(r'^(\w+)')[0] 
    merged_names = []
    sectors = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            long_name = clean_name(info.get("longName", "N/A"))
            sector = info.get("sector", "N/A")
            merged_names.append(f"{ticker} ({long_name})")
            sectors.append(sector)
        except Exception as e:
            # this happens when the yfinance API is rate limited, putting N/A here for now. Happens less when using non multi-threaded getGainers
            merged_names.append(f"{ticker} (N/A)")
            sectors.append("N/A")
    df['Stock'] = [truncate_text(name, 27) for name in merged_names]
    df['Sector'] = [truncate_text(sec, 27) for sec in sectors]

    change_values = df['Premkt Chg'].str.replace('%', '', regex=False).astype(float)
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.axis('off')
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='left',
                     loc='center')

    # Setting column widths
    original_stock_width = table[(0, 0)].get_width()
    narrow_width = original_stock_width * 0.5
    sector_width = narrow_width * 2

    # Row coloring
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#40466e')
            cell.set_text_props(color='w', weight='bold')
            cell.set_fontsize(10)
        else:
            cell.set_facecolor('#f0f0f0' if row % 2 == 0 else 'white')
    premkt_col_index = df.columns.get_loc('Premkt Chg')
    for row in range(1, len(df) + 1):
        val = change_values.iloc[row - 1]
        color = '#c8e6c9' if val > 0 else '#ffcdd2' if val < 0 else 'white'
        table[(row, premkt_col_index)].set_facecolor(color)

    # This is where column widths get set
    for (row, col), cell in table.get_celld().items():
        if col == 0: 
            cell.set_width(original_stock_width)
        elif col == len(df.columns) - 1:  
            cell.set_width(sector_width)
        else: 
            cell.set_width(narrow_width)

    # Add title with today's date
    today_str = datetime.today().strftime("%B %d, %Y")
    plt.title(f"Top Movers in the S&P 500 (Premarket) — {today_str}",
              fontsize=11, fontweight='bold')


    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.3, 1.2)

    # Send visualization over as buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close(fig)
    buf.seek(0)

    return buf


def plot_m2(df):
    """
    Plots the M2 Money Stock over time and returns an in-memory PNG buffer.
    df: DataFrame indexed by DATE with a column 'M2 Money Stock' (string values like '22.02T')
    """

    if isinstance(df.index, pd.PeriodIndex):
        df.index = df.index.to_timestamp()

    # Set to dates
    df = df.copy()
    df = df.reset_index()  
    df['Date'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('Date')

    # Convert T to actual trillions
    df['M2 Money Stock'] = (
        df['M2 Money Stock']
        .str.replace('T', '', regex=False)
        .astype(float)
    )

    fig, ax = plt.subplots(figsize=(7, 5)) 

    # Plot
    ax.plot(df['Date'], df['M2 Money Stock'], color='#2e86ab', linewidth=2)
    ax.fill_between(df['Date'], df['M2 Money Stock'], color='#2e86ab', alpha=0.15)
    ax.set_title("M2 Money Stock Over Time", fontsize=14, fontweight='bold')
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Trillions of USD", fontsize=11)
    y_min = df['M2 Money Stock'].min()
    y_max = df['M2 Money Stock'].max()
    padding = (y_max - y_min) * 0.05
    ax.set_ylim(y_min - padding, y_max + padding)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    # Send visualization over as buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, pad_inches=0.1, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return buf

def plot_price_targets(df):
    """
    Takes a DataFrame with columns:
    ['Last Price', 'Mean Target', 'Median Target', 'High Target', 'Low Target']
    and plots a horizontal bar chart comparing them.
    """
    # Initialize plot
    df = df.copy()
    ticker = df.index[0] if df.index.name or isinstance(df.index[0], str) else ""
    row = df.iloc[0].to_dict()
    metrics = ['Mean Target', 'Median Target', 'High Target', 'Low Target']
    values = [row[m] for m in metrics]
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.barh(metrics, values, color='#4e79a7', alpha=0.8)

    # Add labels
    for bar, val in zip(bars, values):
        ax.text(val, bar.get_y() + bar.get_height()/2,
                f"{val:.2f}",
                va='center', ha='left', fontsize=8)

    # Draw vertical line/label for last price
    ax.axvline(row['Last Price'], color='red', linestyle='--', linewidth=1.5)
    ax.text(row['Last Price'], ax.get_ylim()[0] - 0.15*(ax.get_ylim()[1]-ax.get_ylim()[0]),
        f"Last Price: {row['Last Price']:.2f}",
        color='red', fontsize=8, ha='center', va='top')

    title_str = f"Analyst Price Targets — {ticker}" if ticker else "Analyst Price Targets"
    ax.set_title(title_str, fontsize=12, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Send visualization over as buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, pad_inches=0.1, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def plot_holders(df, ticker):
    """
    Plots major holders data (Insiders %, Institutions %) as a donut chart
    and annotates # of Institutions.
    Returns an in-memory PNG buffer.
    """
    df = df.copy()

    # Extract values
    insiders_pct = float(df["Insiders"].iloc[0].strip('%'))
    institutions_pct = float(df["Institutions"].iloc[0].strip('%'))
    num_institutions = int(df["# of Institutions"].iloc[0])

    # Calculate 'Others' as the rest of the market
    others_pct = 100 - insiders_pct - institutions_pct

    # This was a weird outlier with the API
    if others_pct < 0:
        others_pct = 0

    # Plot donut chart
    labels = ["Insiders", "Institutions", "Others"]
    values = [insiders_pct, institutions_pct, others_pct]
    colors = ["#ff9999", "#66b3ff", "#99ff99"]
    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.3)  # Donut effect
    )

    ax.set_title(f"{ticker} Major Holders Breakdown", fontsize=14, fontweight="bold")

    # Add # of institutions in the center, we could also put the ticker here and put this text below
    plt.text(
        0, 0,
        f"{num_institutions:,}\nInstitutions",
        ha="center", va="center",
        fontsize=11, fontweight="bold"
    )

    plt.tight_layout()

    # Send visualization over as buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return buf

def plot_info(df):
    info_dict = df.iloc[0].to_dict()

    # Format Market Cap as billions with B suffix if numeric
    market_cap = info_dict.get("Market Cap", "N/A")
    if isinstance(market_cap, (int, float)):
        market_cap = f"${market_cap/1e9:.2f}B"
        info_dict["Market Cap"] = market_cap

    # Format Full Time Employees with commas
    fte = info_dict.get("Full Time Employees", "N/A")
    if isinstance(fte, int):
        info_dict["Full Time Employees"] = f"{fte:,}"

    keys = list(info_dict.keys())
    values = [truncate_text(v, max_chars=29) for v in info_dict.values()]  # truncate values only

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.axis('off')

    table = ax.table(
        cellText=list(zip(keys, values)),
        cellLoc='left',
        loc='center'
    )

    for (row, col), cell in table.get_celld().items():
        if col == 0:
            cell.set_text_props(weight='bold', color='#1f497d')  # blue text
            cell.set_facecolor('white')
        else:
            cell.set_text_props(weight='normal', color='black')
            cell.set_facecolor('white')

        # Minimize padding inside cells
        cell.PAD = 0.01  # reduce cell padding (default is larger)

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.3, 1.3)

    plt.title(f"Company Info: {info_dict.get('Company Name', '')}",
              fontsize=14, fontweight='bold', pad=15)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, pad_inches=0.1, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf