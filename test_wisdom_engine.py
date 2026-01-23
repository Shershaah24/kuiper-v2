"""
Test Wisdom Engine with Real MetaAPI Data
==========================================
This script tests the complete Wisdom Engine pipeline:
1. Fetch real OHLCV data from MetaAPI
2. Compute all 161 indicators
3. Run Wisdom Engine analysis
4. Output complete market analysis with reasoning
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load credentials from env.json
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "env.json")
# Fallback to relative path
if not os.path.exists(env_path):
    env_path = "../env.json"

# Try different encodings
for encoding in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
    try:
        with open(env_path, encoding=encoding) as f:
            env = json.load(f)
        break
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue
else:
    # Hardcode credentials as fallback
    env = {
        "METAAPI_TOKEN": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiJkMzNjMjg1NTgxYzY5OTJkYTczZDNmZDZjODNhOTIwMSIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6InRyYWRpbmctYWNjb3VudC1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOmM4NzAyYmI2LWJkMzctNGZjMS04YTU0LTI1ZDY4ZTVmMzFhNiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6Yzg3MDJiYjYtYmQzNy00ZmMxLThhNTQtMjVkNjhlNWYzMWE2Il19LHsiaWQiOiJtZXRhYXBpLXJwYy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDpjODcwMmJiNi1iZDM3LTRmYzEtOGE1NC0yNWQ2OGU1ZjMxYTYiXX0seyJpZCI6Im1ldGFhcGktcmVhbC10aW1lLXN0cmVhbWluZy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDpjODcwMmJiNi1iZDM3LTRmYzEtOGE1NC0yNWQ2OGU1ZjMxYTYiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6Yzg3MDJiYjYtYmQzNy00ZmMxLThhNTQtMjVkNjhlNWYzMWE2Il19LHsiaWQiOiJyaXNrLW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJyaXNrLW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOmM4NzAyYmI2LWJkMzctNGZjMS04YTU0LTI1ZDY4ZTVmMzFhNiJdfV0sImlnbm9yZVJhdGVMaW1pdHMiOmZhbHNlLCJ0b2tlbklkIjoiMjAyMTAyMTMiLCJpbXBlcnNvbmF0ZWQiOmZhbHNlLCJyZWFsVXNlcklkIjoiZDMzYzI4NTU4MWM2OTkyZGE3M2QzZmQ2YzgzYTkyMDEiLCJpYXQiOjE3NjY5ODk5MTksImV4cCI6MTc3NDc2NTkxOX0.LvFCXSkfz6mVHUB2un3-y7eZ-rxvMfaw8iCzmE_y5YKtpwtnMAvF0cRjgTFwKgB3VAS9447IdtZgkpUCTNwq1BdE_SlY43xA7qTD4wxcU3NrQtn98s7UuMffuspdi6Sj0VxYlitiW9h3JNt7yRkgMn6RnIF1pk7FaMQLToFoR4XdEVkBB6ZWW5F4Jwliv6dhwMMqP4rdwzrAc4kFO9MYT7rvfh92Tw9IBMgNZeXVZZ8MvehUAn1X-k2zZVpGNWM7f4eyem-a2DOFOKB2rD8mnXDSIUeMUw2Alm5bkKlRX_9B-fHo2q41-buNTv3DOKt5fxTisBdIJejeFS1334AtUYQ8meFE-YAvUnmjpzsB1yE5rxCMh7imUJbbOrmvCoOOCMojkozcQzEyqM8Fp4vPsjUv2NCWXN2K78Sn758hprt6whiOAlreO-BpuoVEetWcBueagmq83Jagymigf4TgFcKyJFfMHe13erh1DP4Ri2WHq0DucPt80uTStXgmIJpTo7rieKNm8wEX4LkUCpr8kisUCksR2DRmAqqsl_KZrb5rjpiXaqu4-ngyu5VIfhFAVmBZm-PENBJgwPsXz0pZcq8flF8bScOgBAeyaT-qUADOA4_79kkb5c1mdaPAKkoNXj9KcQRJMuvtmnx7vXu10stp8Doa-xuj4zXtBMoiBg8",
        "METAAPI_ACCOUNT_ID": "c8702bb6-bd37-4fc1-8a54-25d68e5f31a6"
    }

# Handle nested structure
if "Variables" in env:
    env = env["Variables"]

os.environ["METAAPI_TOKEN"] = env["METAAPI_TOKEN"]
os.environ["METAAPI_ACCOUNT_ID"] = env["METAAPI_ACCOUNT_ID"]

from src.data_layer import DataLayer
from src.indicators import compute_all_indicators
from src.wisdom_engine import WisdomEngine, analyze_market
from src.models import MarketRegime, TradeDirection


def test_wisdom_engine():
    """Test the complete Wisdom Engine pipeline."""
    print("=" * 70)
    print("KUIPER V2 - WISDOM ENGINE TEST")
    print("=" * 70)
    
    # Initialize data layer
    print("\n[1] Fetching OHLCV data from MetaAPI...")
    data_layer = DataLayer()
    ohlcv = data_layer.get_ohlcv("EURUSD", "H1", bars=500)
    
    if not ohlcv.is_valid():
        print("ERROR: Failed to fetch valid OHLCV data")
        return
    
    print(f"    ✓ Fetched {len(ohlcv)} candles")
    print(f"    ✓ Latest close: {ohlcv.latest_close:.5f}")
    print(f"    ✓ Latest time: {ohlcv.latest_time}")
    
    # Compute all indicators
    print("\n[2] Computing all 161 indicators...")
    import time
    start = time.time()
    indicators = compute_all_indicators(
        ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume
    )
    elapsed = time.time() - start
    print(f"    ✓ Computed in {elapsed:.3f} seconds")
    
    # Run Wisdom Engine
    print("\n[3] Running Wisdom Engine analysis...")
    analysis = analyze_market(
        indicators=indicators,
        current_price=ohlcv.latest_close,
        symbol="EURUSD",
        timeframe="H1",
        account_balance=10000.0
    )
    
    # Output results
    print("\n" + "=" * 70)
    print("MARKET ANALYSIS RESULTS")
    print("=" * 70)
    
    print(f"\nSymbol: {analysis.symbol}")
    print(f"Timeframe: {analysis.timeframe}")
    print(f"Timestamp: {analysis.timestamp}")
    
    print(f"\n{'=' * 70}")
    print("MARKET REGIME")
    print("=" * 70)
    print(f"\nRegime: {analysis.regime.value}")
    print(f"\n{analysis.regime_analysis.reasoning}")
    
    print(f"\n{'=' * 70}")
    print("TRADE DECISION")
    print("=" * 70)
    print(f"\nDirection: {analysis.decision.direction.value}")
    print(f"Position Size Multiplier: {analysis.decision.position_size_multiplier * 100:.0f}%")
    
    print("\nConfidence Factors:")
    for factor in analysis.decision.confidence_factors:
        print(f"  ✓ {factor}")
    
    if analysis.decision.warning_factors:
        print("\nWarning Factors:")
        for factor in analysis.decision.warning_factors:
            print(f"  ⚠ {factor}")
    
    if analysis.parameters and analysis.decision.direction != TradeDirection.NO_TRADE:
        print(f"\n{'=' * 70}")
        print("TRADE PARAMETERS")
        print("=" * 70)
        print(f"\nEntry Price: {analysis.parameters.entry_price:.5f}")
        print(f"Stop Loss: {analysis.parameters.stop_loss:.5f} ({analysis.parameters.stop_loss_pips:.1f} pips)")
        print(f"Take Profit: {analysis.parameters.take_profit:.5f} ({analysis.parameters.take_profit_pips:.1f} pips)")
        print(f"Risk/Reward: 1:{analysis.parameters.risk_reward_ratio:.2f}")
        print(f"Position Size: {analysis.parameters.position_size:.2f} lots")
        print(f"ATR(14): {analysis.parameters.atr_value:.5f}")
    
    print(f"\n{'=' * 70}")
    print("FULL REASONING")
    print("=" * 70)
    print(f"\n{analysis.decision.reasoning}")
    
    # Save full analysis to JSON
    output = {
        "symbol": analysis.symbol,
        "timeframe": analysis.timeframe,
        "timestamp": analysis.timestamp.isoformat(),
        "regime": analysis.regime.value,
        "regime_analysis": {
            "adx_value": analysis.regime_analysis.adx_value,
            "adx_interpretation": analysis.regime_analysis.adx_interpretation,
            "trend_mode": analysis.regime_analysis.trend_mode,
            "trend_mode_interpretation": analysis.regime_analysis.trend_mode_interpretation,
            "ma_alignment": analysis.regime_analysis.ma_alignment,
            "ma_alignment_interpretation": analysis.regime_analysis.ma_alignment_interpretation,
            "volatility_state": analysis.regime_analysis.volatility_state,
            "volatility_interpretation": analysis.regime_analysis.volatility_interpretation,
            "reasoning": analysis.regime_analysis.reasoning
        },
        "decision": {
            "direction": analysis.decision.direction.value,
            "confidence_factors": analysis.decision.confidence_factors,
            "warning_factors": analysis.decision.warning_factors,
            "position_size_multiplier": analysis.decision.position_size_multiplier,
            "reasoning": analysis.decision.reasoning
        },
        "parameters": {
            "entry_price": analysis.parameters.entry_price if analysis.parameters else None,
            "stop_loss": analysis.parameters.stop_loss if analysis.parameters else None,
            "take_profit": analysis.parameters.take_profit if analysis.parameters else None,
            "stop_loss_pips": analysis.parameters.stop_loss_pips if analysis.parameters else None,
            "take_profit_pips": analysis.parameters.take_profit_pips if analysis.parameters else None,
            "risk_reward_ratio": analysis.parameters.risk_reward_ratio if analysis.parameters else None,
            "position_size": analysis.parameters.position_size if analysis.parameters else None,
        } if analysis.parameters else None,
        "interpretations": {
            "trend": analysis.interpretations.trend.interpretation,
            "momentum": analysis.interpretations.momentum.interpretation,
            "volume": analysis.interpretations.volume.interpretation,
            "patterns": analysis.interpretations.patterns.interpretation,
            "cycles": analysis.interpretations.cycles.interpretation
        },
        "key_indicators": {
            "RSI_14": indicators["momentum"]["RSI_14"],
            "ADX_14": indicators["momentum"]["ADX_14"],
            "MACD_hist": indicators["momentum"]["MACD_hist"],
            "HT_TRENDMODE": indicators["cycles"]["HT_TRENDMODE"],
            "ATR_14": indicators["volatility"]["ATR_14"],
            "STOCH_slowk": indicators["momentum"]["STOCH_slowk"],
        }
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wisdom_analysis.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Full analysis saved to: {output_path}")
    print("=" * 70)
    
    return analysis


if __name__ == "__main__":
    test_wisdom_engine()
