"""
Test Overlap Studies Indicators
===============================

Verifies all 18 overlap studies compute correctly with sample data.
"""

import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from indicators.overlap_studies import (
    compute_overlap_studies,
    get_overlap_studies_dict,
    OverlapStudiesResult
)


def generate_sample_ohlcv(n: int = 500) -> tuple:
    """Generate sample OHLCV data for testing."""
    np.random.seed(42)
    
    # Generate realistic price data with trend
    base_price = 1.0850  # EURUSD-like
    returns = np.random.normal(0.0001, 0.001, n)
    close = base_price * np.cumprod(1 + returns)
    
    # Generate OHLC from close
    volatility = np.abs(np.random.normal(0, 0.0005, n))
    high = close + volatility
    low = close - volatility
    open_ = np.roll(close, 1)
    open_[0] = base_price
    
    # Volume
    volume = np.random.uniform(1000, 5000, n)
    
    return open_, high, low, close, volume


def test_overlap_studies_basic():
    """Test basic computation of all overlap studies."""
    open_, high, low, close, volume = generate_sample_ohlcv(500)
    
    result = compute_overlap_studies(open_, high, low, close, volume)
    
    # Check that result is correct type
    assert isinstance(result, OverlapStudiesResult)
    
    # Check SMAs computed
    assert result.sma_20 is not None, "SMA_20 should be computed"
    assert result.sma_50 is not None, "SMA_50 should be computed"
    assert result.sma_200 is not None, "SMA_200 should be computed"
    
    # Check EMAs computed
    assert result.ema_12 is not None, "EMA_12 should be computed"
    assert result.ema_26 is not None, "EMA_26 should be computed"
    assert result.ema_50 is not None, "EMA_50 should be computed"
    
    # Check advanced MAs
    assert result.dema_30 is not None, "DEMA_30 should be computed"
    assert result.tema_30 is not None, "TEMA_30 should be computed"
    assert result.t3_5 is not None, "T3_5 should be computed"
    assert result.wma_30 is not None, "WMA_30 should be computed"
    assert result.trima_30 is not None, "TRIMA_30 should be computed"
    assert result.kama_30 is not None, "KAMA_30 should be computed"
    
    # Check MAMA
    assert result.mama is not None, "MAMA should be computed"
    assert result.fama is not None, "FAMA should be computed"
    
    # Check Hilbert
    assert result.ht_trendline is not None, "HT_TRENDLINE should be computed"
    
    # Check Bollinger Bands
    assert result.bbands_upper is not None, "BBANDS_upper should be computed"
    assert result.bbands_middle is not None, "BBANDS_middle should be computed"
    assert result.bbands_lower is not None, "BBANDS_lower should be computed"
    
    # Check Acceleration Bands
    assert result.accbands_upper is not None, "ACCBANDS_upper should be computed"
    assert result.accbands_middle is not None, "ACCBANDS_middle should be computed"
    assert result.accbands_lower is not None, "ACCBANDS_lower should be computed"
    
    # Check Midpoint/Midprice
    assert result.midpoint_14 is not None, "MIDPOINT_14 should be computed"
    assert result.midprice_14 is not None, "MIDPRICE_14 should be computed"
    
    # Check Parabolic SAR
    assert result.sar is not None, "SAR should be computed"
    assert result.sarext is not None, "SAREXT should be computed"
    
    print("✓ All 18 overlap studies computed successfully!")


def test_overlap_studies_values():
    """Test that computed values are reasonable."""
    open_, high, low, close, volume = generate_sample_ohlcv(500)
    
    result = compute_overlap_studies(open_, high, low, close, volume)
    
    last_close = close[-1]
    
    # SMAs should be near the price
    assert abs(result.sma_20 - last_close) / last_close < 0.05, "SMA_20 should be within 5% of close"
    assert abs(result.sma_50 - last_close) / last_close < 0.10, "SMA_50 should be within 10% of close"
    
    # Bollinger Bands should bracket the price
    assert result.bbands_lower < result.bbands_middle < result.bbands_upper, \
        "Bollinger Bands should be ordered: lower < middle < upper"
    
    # ACCBANDS should bracket the price
    assert result.accbands_lower < result.accbands_middle < result.accbands_upper, \
        "Acceleration Bands should be ordered: lower < middle < upper"
    
    print("✓ Overlap studies values are reasonable!")


def test_overlap_studies_dict():
    """Test dictionary conversion."""
    open_, high, low, close, volume = generate_sample_ohlcv(500)
    
    result = compute_overlap_studies(open_, high, low, close, volume)
    result_dict = get_overlap_studies_dict(result)
    
    # Check all expected keys present
    expected_keys = [
        "SMA_20", "SMA_50", "SMA_200",
        "EMA_12", "EMA_26", "EMA_50",
        "DEMA_30", "TEMA_30", "T3_5",
        "WMA_30", "TRIMA_30", "KAMA_30",
        "MAMA", "FAMA", "HT_TRENDLINE",
        "BBANDS_upper", "BBANDS_middle", "BBANDS_lower",
        "ACCBANDS_upper", "ACCBANDS_middle", "ACCBANDS_lower",
        "MIDPOINT_14", "MIDPRICE_14",
        "SAR", "SAREXT"
    ]
    
    for key in expected_keys:
        assert key in result_dict, f"Missing key: {key}"
    
    print(f"✓ Dictionary has all {len(expected_keys)} expected keys!")


def test_insufficient_data():
    """Test handling of insufficient data."""
    # Only 20 candles - not enough for most indicators
    open_, high, low, close, volume = generate_sample_ohlcv(20)
    
    result = compute_overlap_studies(open_, high, low, close, volume)
    
    # Should return empty result without crashing
    assert isinstance(result, OverlapStudiesResult)
    
    # SMA_200 should be None (not enough data)
    assert result.sma_200 is None, "SMA_200 should be None with only 20 candles"
    
    print("✓ Insufficient data handled gracefully!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("KUIPER V2 - OVERLAP STUDIES TESTS")
    print("="*60 + "\n")
    
    test_overlap_studies_basic()
    test_overlap_studies_values()
    test_overlap_studies_dict()
    test_insufficient_data()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
