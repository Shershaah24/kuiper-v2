# Kuiper V2 - Wisdom-Based Trading Engine

A sophisticated trading system that computes ALL 161 TA-Lib indicators and makes **intelligent trading decisions** based on complete market understanding.

## Key Features

- **161 TA-Lib Indicators**: Complete implementation of all technical indicators
- **Wisdom Engine**: Context-aware interpretation of indicators (NOT confidence scoring)
- **Market Regime Detection**: TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE
- **Full Reasoning**: Every trade decision includes detailed explanation
- **MetaAPI Integration**: Real-time data and trade execution
- **AWS Lambda Ready**: Deploy as serverless function with EventBridge scheduling

## Philosophy

This is NOT a confidence-based scoring system. The Wisdom Engine:

1. **UNDERSTANDS** what each indicator means in context
2. **DETERMINES** market regime first
3. **INTERPRETS** indicators differently based on regime
4. **SYNTHESIZES** all information into a wise decision
5. **EXPLAINS** the reasoning for every decision

### Example: RSI = 30

- In **TRENDING_UP**: "Pullback opportunity, not reversal"
- In **RANGING**: "Oversold at range bottom, potential long"
- In **TRENDING_DOWN**: "Strong momentum, trend continuation"

## Project Structure

```
kuiper-v2/
├── src/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Configuration and environment variables
│   ├── data_layer.py         # MetaAPI data fetching with caching
│   ├── models.py             # Data classes for analysis and trades
│   ├── wisdom_engine.py      # The brain - market analysis and decisions
│   ├── trade_executor.py     # Trade execution via MetaAPI
│   ├── handler.py            # Lambda handler and KuiperEngine
│   └── indicators/           # All 161 TA-Lib indicators
│       ├── __init__.py
│       ├── overlap_studies.py    # 18 indicators (SMA, EMA, BBANDS, etc.)
│       ├── momentum.py           # 31 indicators (RSI, MACD, ADX, etc.)
│       ├── volume.py             # 3 indicators (AD, ADOSC, OBV)
│       ├── volatility.py         # 3 indicators (ATR, NATR, TRANGE)
│       ├── cycles.py             # 5 indicators (HT_* functions)
│       ├── price_transform.py    # 5 indicators (AVGPRICE, etc.)
│       ├── statistics.py         # 9 indicators (LINEARREG, etc.)
│       ├── patterns.py           # 61 candlestick patterns (CDL*)
│       ├── math_transform.py     # 15 math functions
│       └── math_operators.py     # 11 math operators
├── tests/
├── test_all_indicators.py    # Test all indicators with real data
├── test_wisdom_engine.py     # Test Wisdom Engine analysis
├── test_full_pipeline.py     # Test complete trading pipeline
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Note: TA-Lib requires the C library to be installed first.

### 2. Set Environment Variables

```bash
export METAAPI_TOKEN="your_token"
export METAAPI_ACCOUNT_ID="your_account_id"
```

### 3. Run Tests

```bash
# Test all indicators
python test_all_indicators.py

# Test Wisdom Engine
python test_wisdom_engine.py

# Test full pipeline (dry run)
python test_full_pipeline.py
```

## Usage

### Basic Analysis

```python
from src import DataLayer, compute_all_indicators, analyze_market

# Fetch data
data_layer = DataLayer()
ohlcv = data_layer.get_ohlcv("EURUSD", "H1", bars=500)

# Compute all indicators
indicators = compute_all_indicators(
    ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume
)

# Run Wisdom Engine analysis
analysis = analyze_market(
    indicators=indicators,
    current_price=ohlcv.latest_close,
    symbol="EURUSD",
    timeframe="H1"
)

print(f"Regime: {analysis.regime.value}")
print(f"Decision: {analysis.decision.direction.value}")
print(f"Reasoning: {analysis.decision.reasoning}")
```

### Full Pipeline

```python
from src import KuiperEngine

# Initialize engine (dry_run=True for testing)
engine = KuiperEngine(dry_run=True, account_balance=10000.0)

# Process single symbol
result = engine.process_symbol("EURUSD", "H1")

# Process multiple symbols in parallel
results = engine.process_all_symbols(
    symbols=["EURUSD", "GBPUSD", "USDJPY"],
    timeframe="H1",
    parallel=True
)
```

### Lambda Handler

```python
from src import handler

# Invoke Lambda
result = handler({
    "symbols": ["EURUSD", "GBPUSD"],
    "timeframe": "H1",
    "dry_run": True
}, None)
```

## Market Regime Detection

The Wisdom Engine determines market regime using:

| Indicator | TRENDING_UP | TRENDING_DOWN | RANGING | VOLATILE |
|-----------|-------------|---------------|---------|----------|
| ADX | > 25 | > 25 | < 20 | Any |
| +DI vs -DI | +DI > -DI | -DI > +DI | Close | Any |
| HT_TRENDMODE | 1 | 1 | 0 | Any |
| MA Alignment | Bullish | Bearish | Mixed | Any |
| ATR | Normal | Normal | Normal | Spike > 2x |

## Trade Decision Hierarchy

When indicators conflict, the hierarchy is:

1. **Regime** (highest priority)
2. **Trend Indicators**
3. **Momentum Indicators**
4. **Volume Indicators**
5. **Pattern Indicators** (lowest priority)

## Risk Management

- Stop Loss: 1.5-2x ATR from entry
- Take Profit: 2-3x ATR (minimum 1:1.5 R:R)
- Position Size: Max 2% account risk per trade
- Ranging markets: 50% position size

## Performance

- Single symbol: ~1.2 seconds
- 10 symbols (parallel): ~18 seconds
- All 161 indicators: ~0.015 seconds

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| METAAPI_TOKEN | - | MetaAPI authentication token |
| METAAPI_ACCOUNT_ID | - | MetaAPI account ID |
| SYMBOLS | Major pairs | Comma-separated symbol list |
| TIMEFRAME | H1 | Default timeframe |
| DRY_RUN | true | Disable real trading |
| ATR_SL_MULTIPLIER | 1.5 | ATR multiplier for stop loss |
| ATR_TP_MULTIPLIER | 2.5 | ATR multiplier for take profit |
| MAX_RISK_PERCENT | 2.0 | Maximum risk per trade |

## License

MIT
