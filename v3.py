import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculates RSI using Wilder's Smoothing method."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def run_backtest(start_date="2019-01-01", end_date="2026-01-01", initial_cash=100000.0, default_holding="SPY"):
    tickers = list(set([
        "UVXY", "VIXM", "SPXL", "QLD", "BIL", "SSO", default_holding,
        "QQQE", "VTV", "VOX", "TECL", "VOOG", "VOOV", "XLP", "TQQQ", "XLY", "FAS", "SPY", "SOXL"
    ]))

    print("Fetching market data...")
    raw_data = yf.download(tickers, start="2018-11-01", end=end_date, auto_adjust=True)
    
    if "Close" in raw_data.columns.levels[0]:
        data = raw_data["Close"].ffill().dropna()
    else:
        data = raw_data.ffill().dropna()

    # Calculate RSI indicators
    rsi = {}
    rsi[("QQQE", 10)] = calculate_rsi(data["QQQE"], 10)
    rsi[("VTV", 10)]  = calculate_rsi(data["VTV"], 10)
    rsi[("VOX", 10)]  = calculate_rsi(data["VOX"], 10)
    rsi[("TECL", 10)] = calculate_rsi(data["TECL"], 10)
    rsi[("VOOG", 10)] = calculate_rsi(data["VOOG"], 10)
    rsi[("VOOV", 10)] = calculate_rsi(data["VOOV"], 10)
    rsi[("XLP", 10)]  = calculate_rsi(data["XLP"], 10)
    rsi[("TQQQ", 10)] = calculate_rsi(data["TQQQ"], 10)
    rsi[("XLY", 10)]  = calculate_rsi(data["XLY"], 10)
    rsi[("FAS", 10)]  = calculate_rsi(data["FAS"], 10)
    rsi[("SPY", 10)]  = calculate_rsi(data["SPY"], 10)
    rsi[("SOXL", 10)] = calculate_rsi(data["SOXL"], 10)
    rsi[("SPXL", 10)] = calculate_rsi(data["SPXL"], 10)
    rsi[("UVXY", 21)] = calculate_rsi(data["UVXY"], 21)
    rsi[("SPY", 21)]  = calculate_rsi(data["SPY"], 21)

    overbought_checks = [
        ("QQQE", 10, 79), ("VTV", 10, 79), ("VOX", 10, 79),
        ("TECL", 10, 79), ("VOOG", 10, 79), ("VOOV", 10, 79),
        ("XLP", 10, 75),  ("TQQQ", 10, 79), ("XLY", 10, 80),
        ("FAS", 10, 80),  ("SPY", 10, 80)
    ]

    backtest_dates = data.loc[start_date:].index
    
    portfolio_value = [initial_cash]
    current_cash = initial_cash
    current_shares = 0
    current_holding = None
    
    dates_tracked = [backtest_dates[0]]
    trade_logs = []

    def determine_target(date):
        for ticker, period, threshold in overbought_checks:
            val = rsi[(ticker, period)].loc[date]
            if not np.isnan(val) and val > threshold:
                return "UVXY"

        uvxy_rsi21 = rsi[("UVXY", 21)].loc[date]
        if not np.isnan(uvxy_rsi21) and uvxy_rsi21 > 65:
            spy_rsi21 = rsi[("SPY", 21)].loc[date]
            if not np.isnan(spy_rsi21) and spy_rsi21 > 30:
                return "VIXM"
            else:
                return "SPXL"

        tqqq_rsi10 = rsi[("TQQQ", 10)].loc[date]
        if not np.isnan(tqqq_rsi10) and tqqq_rsi10 < 30:
            return "QLD"

        soxl_rsi10 = rsi[("SOXL", 10)].loc[date]
        if not np.isnan(soxl_rsi10) and soxl_rsi10 < 30:
            return "BIL"

        spxl_rsi10 = rsi[("SPXL", 10)].loc[date]
        if not np.isnan(spxl_rsi10) and spxl_rsi10 < 30:
            return "SSO"

        return default_holding

    # Simulation with trade logging
    for i in range(1, len(backtest_dates)):
        prev_date = backtest_dates[i - 1]
        curr_date = backtest_dates[i]

        target = determine_target(prev_date)

        if target != current_holding:
            # Sell existing asset
            if current_holding is not None:
                exit_price = data[current_holding].loc[curr_date]
                current_cash = current_shares * exit_price
                
                trade_logs.append({
                    "Date": curr_date.strftime("%Y-%m-%d"),
                    "Action": "SELL",
                    "Ticker": current_holding,
                    "Shares": round(current_shares, 4),
                    "Price": round(exit_price, 2),
                    "Value": round(current_cash, 2)
                })

            # Buy new asset
            current_holding = target
            entry_price = data[current_holding].loc[curr_date]
            current_shares = current_cash / entry_price

            trade_logs.append({
                "Date": curr_date.strftime("%Y-%m-%d"),
                "Action": "BUY",
                "Ticker": current_holding,
                "Shares": round(current_shares, 4),
                "Price": round(entry_price, 2),
                "Value": round(current_cash, 2)
            })

        current_equity = current_shares * data[current_holding].loc[curr_date]
        portfolio_value.append(current_equity)
        dates_tracked.append(curr_date)

    # Export Trade CSV
    trades_df = pd.DataFrame(trade_logs)
    trades_df.to_csv("trade_log.csv", index=False)
    print("Trade log exported to 'trade_log.csv'.")

    # Save Equity Curve Plot
    equity_df = pd.DataFrame({"Equity": portfolio_value}, index=dates_tracked)
    spy_initial_shares = initial_cash / data["SPY"].loc[backtest_dates[0]]
    equity_df["SPY_Benchmark"] = data["SPY"].loc[backtest_dates] * spy_initial_shares

    plt.style.use("seaborn-v0_8-darkgrid" if "seaborn-v0_8-darkgrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    ax.plot(equity_df.index, equity_df["Equity"], label="Strategy", color="#1f77b4", linewidth=2)
    ax.plot(equity_df.index, equity_df["SPY_Benchmark"], label="SPY Benchmark", color="#7f7f7f", linestyle="--", linewidth=1.5)

    ax.set_title("Single Popped Dividends Strategy Performance", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Portfolio Value ($)", fontsize=11)
    ax.yaxis.set_major_formatter("${x:,.0f}")
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig("real_equity_curve.jpg", format="jpg", dpi=300)
    plt.close()

if __name__ == "__main__":
    run_backtest()