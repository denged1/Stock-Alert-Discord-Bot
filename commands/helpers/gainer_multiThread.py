import math
import pandas as pd
import concurrent.futures
from commands.helpers.filter_gainers import download_data
from commands.helpers.utility import format_percentage, format_large_num, normalize_ticker

def chunked(seq, n_chunks):
    n = max(1, n_chunks)
    size = math.ceil(len(seq) / n)
    return [seq[i:i+size] for i in range(0, len(seq), size)]

def _process_chunk(tickers_chunk):
    rows = []
    for t in tickers_chunk:
        try:
            # Expect download_data to return: (ticker, pct_change_float, market_cap_float, volume_float_or_int)
            sym, pct, mcap, vol = download_data(normalize_ticker(t))
            rows.append((sym, pct, mcap, vol))
        except Exception as e:
            # Swallow per-ticker errors; log if you want
            # logging.warning(f"{t}: {e}")
            rows.append((t, None, None, None))
        # tiny pacing to be gentle on Yahoo; adjust/remove if you want
        # time.sleep(0.02)
    return rows

def getGainers_mt(tickers: list[str], min_market_cap=1e9, workers: int = 4) -> pd.DataFrame:
    """
    Multithreaded gainers fetch.
    - Partitions tickers into `workers` chunks
    - Each thread processes its chunk and returns raw rows
    - Merge & post-process at the end to avoid race conditions
    """
    if not tickers:
        return pd.DataFrame(columns=['Tckr', 'Premkt Chg', 'Mkt Cap', 'Volume'])

    chunks = chunked(tickers, workers)
    all_rows = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_process_chunk, ch) for ch in chunks]
        for f in concurrent.futures.as_completed(futures):
            all_rows.extend(f.result())

    # Filter rows safely: allow 0.0 pct_change; require non-None and cap threshold
    filtered = [
        (t, pct, mcap, vol)
        for (t, pct, mcap, vol) in all_rows
        if (pct is not None) and (mcap is not None) and (mcap > min_market_cap)
    ]

    if not filtered:
        return pd.DataFrame(columns=['Tckr', 'Premkt Chg', 'Mkt Cap', 'Volume'])

    # Sort by pct change desc
    filtered.sort(key=lambda r: r[1], reverse=True)



    # Build final rows with display strings
    display = [
        (t, format_percentage(pct), format_large_num(mcap), format_large_num(vol))
        for (t, pct, mcap, vol) in filtered
    ]

    return pd.DataFrame(display, columns=['Tckr', 'Premkt Chg', 'Mkt Cap', 'Volume'])
