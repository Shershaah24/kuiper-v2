"""
Test Full Kuiper V2 Pipeline
============================
Tests the complete trading pipeline:
1. Data fetching from MetaAPI
2. All 161 indicator computation
3. Wisdom Engine analysis
4. Trade execution (dry run)
"""

import json
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load credentials
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "env.json")
for encoding in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
    try:
        with open(env_path, encoding=encoding) as f:
            env = json.load(f)
        break
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue
else:
    env = {
        "METAAPI_TOKEN": os.environ.get("METAAPI_TOKEN", ""),
        "METAAPI_ACCOUNT_ID": os.environ.get("METAAPI_ACCOUNT_ID", "")
    }

if "Variables" in env:
    env = env["Variables"]

os.environ["METAAPI_TOKEN"] = env.get("METAAPI_TOKEN", "")
os.environ["METAAPI_ACCOUNT_ID"] = env.get("METAAPI_ACCOUNT_ID", "")

from src.handler import KuiperEngine


def test_full_pipeline():
    """Test the complete Kuiper V2 pipeline."""
    print("=" * 70)
    print("KUIPER V2 - FULL PIPELINE TEST")
    print("=" * 70)
    
    # Initialize engine in dry run mode
    print("\n[1] Initializing Kuiper Engine (DRY RUN mode)...")
    engine = KuiperEngine(dry_run=True, account_balance=10000.0)
    print("    ✓ Engine initialized")
    
    # Test single symbol
    print("\n[2] Testing single symbol (EURUSD)...")
    start = time.time()
    result = engine.process_symbol("EURUSD", "H1")
    elapsed = time.time() - start
    
    print(f"    ✓ Processed in {elapsed:.3f} seconds")
    print(f"    ✓ Success: {result['success']}")
    
    if result['success']:
        analysis = result['analysis']
        print(f"\n    ANALYSIS RESULTS:")
        print(f"    - Regime: {analysis['regime']}")
        print(f"    - Decision: {analysis['decision']}")
        print(f"    - Position Size: {analysis['position_size_multiplier'] * 100:.0f}%")
        
        if result['trade_result']:
            trade = result['trade_result']
            print(f"\n    TRADE RESULT:")
            print(f"    - Direction: {trade['direction']}")
            print(f"    - Entry: {trade['entry_price']}")
            print(f"    - Stop Loss: {trade['stop_loss']}")
            print(f"    - Take Profit: {trade['take_profit']}")
            print(f"    - Lot Size: {trade['lot_size']}")
            print(f"    - Order ID: {trade['order_id']}")
    else:
        print(f"    ✗ Error: {result['error']}")
    
    # Test multiple symbols
    print("\n[3] Testing multiple symbols...")
    test_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    start = time.time()
    results = engine.process_all_symbols(
        symbols=test_symbols,
        timeframe="H1",
        parallel=True
    )
    elapsed = time.time() - start
    
    print(f"    ✓ Processed {results['symbols_processed']} symbols in {elapsed:.3f} seconds")
    print(f"    ✓ Trades executed: {results['trades_executed']}")
    print(f"    ✓ Errors: {results['errors']}")
    
    print("\n    INDIVIDUAL RESULTS:")
    for symbol, res in results['results'].items():
        if res['success']:
            analysis = res['analysis']
            decision = analysis['decision']
            regime = analysis['regime']
            print(f"    - {symbol}: {regime} → {decision}")
        else:
            print(f"    - {symbol}: ERROR - {res['error']}")
    
    # Save full results
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'=' * 70}")
    print(f"Full results saved to: {output_path}")
    print("=" * 70)
    
    return results


def test_performance():
    """Test performance with 10 symbols."""
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST - 10 SYMBOLS")
    print("=" * 70)
    
    engine = KuiperEngine(dry_run=True, account_balance=10000.0)
    
    symbols = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
        "USDCHF", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"
    ]
    
    print(f"\nProcessing {len(symbols)} symbols in parallel...")
    start = time.time()
    results = engine.process_all_symbols(symbols=symbols, parallel=True)
    elapsed = time.time() - start
    
    print(f"\n    Total time: {elapsed:.2f} seconds")
    print(f"    Average per symbol: {elapsed/len(symbols):.2f} seconds")
    print(f"    Symbols processed: {results['symbols_processed']}")
    print(f"    Trades executed: {results['trades_executed']}")
    print(f"    Errors: {results['errors']}")
    
    # Check if we meet the 30 second target
    if elapsed < 30:
        print(f"\n    ✓ PASSED: Under 30 second target ({elapsed:.2f}s)")
    else:
        print(f"\n    ✗ FAILED: Over 30 second target ({elapsed:.2f}s)")
    
    return results


if __name__ == "__main__":
    test_full_pipeline()
    test_performance()
