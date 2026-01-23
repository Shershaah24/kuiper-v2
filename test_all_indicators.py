"""
Test All 161 TA-Lib Indicators with Real MetaAPI Data
=====================================================

This script fetches real OHLCV data from MetaAPI and computes
all 161 indicators to verify they work correctly.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import time
import numpy as np

# MetaAPI credentials from environment
METAAPI_TOKEN = os.environ.get("METAAPI_TOKEN", "")
METAAPI_ACCOUNT_ID = os.environ.get("METAAPI_ACCOUNT_ID", "")
METAAPI_MARKET_DATA_URL = "https://mt-market-data-client-api-v1.new-york.agiliumtrade.ai"


def fetch_ohlcv(symbol: str, timeframe: str, bars: int = 500):
    """Fetch OHLCV data from MetaAPI."""
    
    tf_map = {
        "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
        "H1": "1h", "H4": "4h", "D1": "1d"
    }
    tf = tf_map.get(timeframe, timeframe.lower())
    
    url = (f"{METAAPI_MARKET_DATA_URL}/users/current/accounts/{METAAPI_ACCOUNT_ID}"
           f"/historical-market-data/symbols/{symbol}/timeframes/{tf}"
           f"/candles?limit={bars}")
    
    req = urllib.request.Request(url)
    req.add_header("auth-token", METAAPI_TOKEN)
    req.add_header("Accept", "application/json")
    
    with urllib.request.urlopen(req, timeout=30) as response:
        candles = json.loads(response.read().decode())
    
    # Parse into numpy arrays
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    times = []
    
    for c in candles:
        if c.get('close') is not None:
            opens.append(float(c.get('open', c['close'])))
            highs.append(float(c.get('high', c['close'])))
            lows.append(float(c.get('low', c['close'])))
            closes.append(float(c['close']))
            volumes.append(float(c.get('tickVolume', 0)))
            times.append(c.get('time', ''))
    
    return {
        'open': np.array(opens, dtype=np.float64),
        'high': np.array(highs, dtype=np.float64),
        'low': np.array(lows, dtype=np.float64),
        'close': np.array(closes, dtype=np.float64),
        'volume': np.array(volumes, dtype=np.float64),
        'time': times
    }


# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'indicators'))

import talib
from overlap_studies import compute_overlap_studies, get_overlap_studies_dict
from momentum import compute_momentum, get_momentum_dict
from volume import compute_volume, get_volume_dict
from volatility import compute_volatility, get_volatility_dict
from cycles import compute_cycles, get_cycles_dict
from price_transform import compute_price_transform, get_price_transform_dict
from statistics import compute_statistics, get_statistics_dict
from patterns import compute_patterns, get_patterns_dict
from math_transform import compute_math_transform, get_math_transform_dict
from math_operators import compute_math_operators, get_math_operators_dict


def compute_all_indicators(open_, high, low, close, volume):
    """Compute all indicators."""
    overlap_result = compute_overlap_studies(open_, high, low, close, volume)
    momentum_result = compute_momentum(open_, high, low, close, volume)
    volume_result = compute_volume(open_, high, low, close, volume)
    volatility_result = compute_volatility(open_, high, low, close, volume)
    cycles_result = compute_cycles(open_, high, low, close, volume)
    price_transform_result = compute_price_transform(open_, high, low, close, volume)
    statistics_result = compute_statistics(open_, high, low, close, volume)
    patterns_result = compute_patterns(open_, high, low, close, volume)
    math_transform_result = compute_math_transform(open_, high, low, close, volume)
    math_operators_result = compute_math_operators(open_, high, low, close, volume)
    
    return {
        "overlap": get_overlap_studies_dict(overlap_result),
        "momentum": get_momentum_dict(momentum_result),
        "volume": get_volume_dict(volume_result),
        "volatility": get_volatility_dict(volatility_result),
        "cycles": get_cycles_dict(cycles_result),
        "price_transform": get_price_transform_dict(price_transform_result),
        "statistics": get_statistics_dict(statistics_result),
        "patterns": get_patterns_dict(patterns_result),
        "math_transform": get_math_transform_dict(math_transform_result),
        "math_operators": get_math_operators_dict(math_operators_result),
    }


def test_all_indicators():
    """Fetch data and compute all indicators."""
    
    print("=" * 80)
    print("KUIPER V2 - ALL 161 TA-LIB INDICATORS TEST")
    print("=" * 80)
    
    # Check credentials
    if not METAAPI_TOKEN or not METAAPI_ACCOUNT_ID:
        print("\n❌ ERROR: MetaAPI credentials not set!")
        print("Set METAAPI_TOKEN and METAAPI_ACCOUNT_ID environment variables")
        return
    
    print(f"\n✓ MetaAPI Token: {METAAPI_TOKEN[:20]}...")
    print(f"✓ Account ID: {METAAPI_ACCOUNT_ID}")
    
    # Fetch data
    print("\n" + "-" * 40)
    print("FETCHING DATA FROM METAAPI...")
    print("-" * 40)
    
    symbol = "EURUSD"
    timeframe = "H1"
    bars = 500
    
    print(f"\nFetching {bars} bars of {symbol} {timeframe}...")
    
    try:
        ohlcv = fetch_ohlcv(symbol, timeframe, bars)
    except Exception as e:
        print(f"❌ ERROR fetching data: {e}")
        return
    
    print(f"✓ Received {len(ohlcv['close'])} candles")
    print(f"✓ Latest close: {ohlcv['close'][-1]:.5f}")
    print(f"✓ Latest time: {ohlcv['time'][-1]}")
    
    # Compute all indicators
    print("\n" + "-" * 40)
    print("COMPUTING ALL 161 INDICATORS...")
    print("-" * 40)
    
    start_time = time.time()
    
    indicators = compute_all_indicators(
        ohlcv['open'],
        ohlcv['high'],
        ohlcv['low'],
        ohlcv['close'],
        ohlcv['volume']
    )
    
    elapsed = time.time() - start_time
    print(f"\n✓ Computation time: {elapsed:.3f} seconds")
    
    # Print results by category
    print("\n" + "=" * 80)
    print("INDICATOR RESULTS")
    print("=" * 80)
    
    for category, values in indicators.items():
        print(f"\n{'─' * 40}")
        print(f"📊 {category.upper()}")
        print(f"{'─' * 40}")
        
        if isinstance(values, dict):
            # Handle patterns specially
            if category == "patterns":
                patterns_dict = values.get("patterns", {})
                bullish = values.get("bullish_patterns", [])
                bearish = values.get("bearish_patterns", [])
                
                print(f"  Total patterns checked: {len(patterns_dict)}")
                print(f"  Bullish patterns detected: {len(bullish)}")
                if bullish:
                    for p in bullish:
                        print(f"    ✅ {p}")
                print(f"  Bearish patterns detected: {len(bearish)}")
                if bearish:
                    for p in bearish:
                        print(f"    🔻 {p}")
            else:
                for key, value in values.items():
                    if value is not None:
                        if isinstance(value, float):
                            print(f"  {key}: {value:.5f}")
                        else:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: None")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Count values
    total_computed = 0
    total_null = 0
    
    for category, values in indicators.items():
        if isinstance(values, dict):
            if category == "patterns":
                total_computed += len(values.get("patterns", {}))
            else:
                for key, value in values.items():
                    if value is not None:
                        total_computed += 1
                    else:
                        total_null += 1
    
    print(f"\n✓ Successfully computed: {total_computed} indicator values")
    print(f"⚠ Null values: {total_null}")
    print(f"⏱ Total time: {elapsed:.3f} seconds")
    
    # Save to JSON
    output_file = "indicator_output.json"
    
    json_output = {
        "symbol": symbol,
        "timeframe": timeframe,
        "bars": len(ohlcv['close']),
        "latest_close": float(ohlcv['close'][-1]),
        "latest_time": ohlcv['time'][-1],
        "computation_time_seconds": elapsed,
        "indicators": indicators
    }
    
    with open(output_file, 'w') as f:
        json.dump(json_output, f, indent=2, default=str)
    
    print(f"\n✓ Full output saved to: {output_file}")
    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    test_all_indicators()
