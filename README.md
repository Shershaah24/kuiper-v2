# Kuiper V2 - Wisdom-Based Trading Engine

A sophisticated forex trading system that computes all 159 TA-Lib technical indicators and makes intelligent trading decisions based on complete market understanding.

## 🧠 Philosophy

Unlike confidence-based systems that simply score indicators, Kuiper V2 **UNDERSTANDS** what each indicator is telling it about the market state. It synthesizes all 159 indicators into a complete market picture and makes trading decisions based on that comprehensive understanding.

## 🎯 Key Features

- **159 TA-Lib Indicators**: Complete technical analysis coverage
- **Market Regime Detection**: Automatically identifies Trending Up, Trending Down, Ranging, or Volatile markets
- **Wisdom-Based Decisions**: Context-aware indicator interpretation
- **Full Reasoning Output**: Every trade decision includes detailed explanation
- **MetaAPI Integration**: Real-time forex data and trade execution
- **AWS Lambda Deployment**: Serverless, scheduled execution

## 📊 Indicator Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Overlap Studies | 18 | Trend identification (SMA, EMA, BBANDS, etc.) |
| Momentum | 31 | Momentum analysis (RSI, MACD, ADX, etc.) |
| Volume | 3 | Volume confirmation (OBV, AD, ADOSC) |
| Volatility | 3 | Volatility assessment (ATR, NATR, TRANGE) |
| Cycle | 5 | Market cycle detection (Hilbert Transform) |
| Pattern Recognition | 61 | Candlestick patterns (all CDL* functions) |
| Statistics | 9 | Statistical analysis |
| Price Transform | 5 | Price calculations |
| Math Transform | 15 | Mathematical operations |
| Math Operators | 11 | Arithmetic operations |

## 🔄 How It Works

```
MetaAPI OHLCV Data
        │
        ▼
┌───────────────────┐
│  Indicator Engine │ ──► Compute all 159 indicators
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Wisdom Engine   │ ──► Detect Market Regime
│                   │ ──► Interpret each indicator in context
│                   │ ──► Synthesize into wise decision
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Trade Executor   │ ──► Execute via MetaAPI with SL/TP
└───────────────────┘
```

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Shershaah24/kuiper-v2.git
cd kuiper-v2

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export METAAPI_TOKEN=your_token
export METAAPI_ACCOUNT_ID=your_account_id

# Run locally
python -m src.handler
```

## 📁 Project Structure

```
kuiper-v2/
├── src/
│   ├── __init__.py
│   ├── handler.py          # Lambda entry point
│   ├── data_layer.py       # MetaAPI data fetching
│   ├── indicator_engine.py # All 159 TA-Lib computations
│   ├── wisdom_engine.py    # Market understanding & decisions
│   ├── trade_executor.py   # Trade execution
│   ├── models.py           # Data models
│   └── config.py           # Configuration
├── tests/
│   └── ...
├── infrastructure/
│   └── template.yaml       # SAM template
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `METAAPI_TOKEN` | MetaAPI authentication token | Required |
| `METAAPI_ACCOUNT_ID` | MetaAPI account ID | Required |
| `SYMBOLS` | Comma-separated currency pairs | EURUSD,GBPUSD,USDJPY |
| `TIMEFRAME` | Trading timeframe | H1 |
| `RSI_PERIOD` | RSI calculation period | 14 |
| `ATR_MULTIPLIER_SL` | ATR multiplier for stop loss | 1.5 |
| `ATR_MULTIPLIER_TP` | ATR multiplier for take profit | 2.5 |

## 📜 License

MIT License
