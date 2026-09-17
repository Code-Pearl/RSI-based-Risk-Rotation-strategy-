# Single Popped Dividends Strategy Backtest

A momentum and mean-reversion backtest strategy that rotates between leveraged ETFs, sector funds, and volatility hedges based on RSI signals.

## Overview

This project implements a rule-based tactical allocation strategy that switches a portfolio between multiple ETFs depending on overbought/oversold RSI conditions across a basket of equity, sector, and volatility instruments.

## Strategy Logic

The strategy evaluates a set of RSI-based signals each day and selects a target holding:

### Overbought Rotation → `UVXY`
If any of the following assets have RSI(10) above their threshold, rotate into **UVXY** (volatility hedge):

| Ticker | RSI Period | Threshold |
|--------|-----------|-----------|
| QQQE   | 10        | 79        |
| VTV    | 10        | 79        |
| VOX    | 10        | 79        |
| TECL   | 10        | 79        |
| VOOG   | 10        | 79        |
| VOOV   | 10        | 79        |
| XLP    | 10        | 75        |
| TQQQ   | 10        | 79        |
| XLY    | 10        | 80        |
| FAS    | 10        | 80        |
| SPY    | 10        | 80        |

### Volatility Regime → `VIXM` or `SPXL`
- If **UVXY RSI(21) > 65**:
  - If **SPY RSI(21) > 30** → hold **VIXM**
  - Otherwise → hold **SPXL**

### Oversold Dips
- **TQQQ RSI(10) < 30** → hold **QLD**
- **SOXL RSI(10) < 30** → hold **BIL**
- **SPXL RSI(10) < 30** → hold **SSO**

### Default
- Otherwise → hold the default holding (default: **SPY**)

## Universe

```
UVXY, VIXM, SPXL, QLD, BIL, SSO, SPY,
QQQE, VTV, VOX, TECL, VOOG, VOOV,
XLP, TQQQ, XLY, FAS, SOXL
```

## Features

- **Wilder's RSI** calculation using exponential weighted moving averages
- **Daily signal evaluation** with next-day execution (uses previous day's RSI to decide today's target)
- **Trade logging** exported to `trade_log.csv`
- **Equity curve** plotted against a SPY buy-and-hold benchmark
- **High-resolution chart** saved as `real_equity_curve.jpg`

## Installation

```bash
pip install pandas numpy yfinance matplotlib
```

## Usage

```bash
python v3.py
```

### Configuration

Edit the `run_backtest()` call in `__main__` or pass arguments directly:

```python
run_backtest(
    start_date="2019-01-01",
    end_date="2026-01-01",
    initial_cash=100000.0,
    default_holding="SPY"
)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `start_date` | `"2019-01-01"` | Backtest start date |
| `end_date` | `"2026-01-01"` | Backtest end date |
| `initial_cash` | `100000.0` | Starting portfolio value |
| `default_holding` | `"SPY"` | Fallback asset when no signal fires |

## Outputs

| File | Description |
|------|-------------|
| `trade_log.csv` | Every BUY/SELL with date, ticker, shares, price, value |
| `real_equity_curve.jpg` | Strategy equity vs. SPY benchmark |

## How It Works

1. **Data Fetch** — Downloads adjusted close prices from Yahoo Finance starting one month before the backtest start (to warm up RSI calculations).
2. **RSI Computation** — Calculates RSI(10) and RSI(21) for all relevant tickers using Wilder's smoothing.
3. **Signal Evaluation** — On each day, `determine_target()` checks conditions in priority order and returns the target ticker.
4. **Rebalancing** — If the target differs from the current holding, the portfolio sells the old asset and buys the new one at the current close.
5. **Tracking** — Daily portfolio equity is recorded and compared against a SPY buy-and-hold benchmark.

## Notes & Caveats

- ⚠️ **Lookahead-free by design**: Signals use the *previous* day's RSI to decide the *current* day's allocation.
- ⚠️ **No transaction costs, slippage, or taxes** are modeled — real-world results will differ.
- ⚠️ **Leveraged ETFs** (TQQQ, SOXL, SPXL, TECL, FAS, QLD, SSO) carry significant decay and risk.
- ⚠️ **Volatility products** (UVXY, VIXM) are subject to severe contango decay over time.
- This is a **research/educational tool**, not investment advice.

## Disclaimer

This software is provided for educational and research purposes only. Past performance does not guarantee future results. Leveraged and volatility ETFs are highly risky instruments. Do your own due diligence before trading any strategy.

## License

License — see `LICENSE` for details.
