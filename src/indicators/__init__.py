"""
Kuiper V2 - Technical Indicators Package
=========================================

COMPLETE implementation of ALL 161 TA-Lib indicators organized by category.

Categories:
- Overlap Studies (18 functions): Moving averages, Bollinger Bands, SAR
- Momentum (31 functions): RSI, MACD, ADX, Stochastic, etc.
- Volume (3 functions): AD, ADOSC, OBV
- Volatility (3 functions): ATR, NATR, TRANGE
- Cycles (5 functions): Hilbert Transform indicators
- Price Transform (5 functions): AVGPRICE, TYPPRICE, etc.
- Statistics (9 functions): Linear regression, STDDEV, etc.
- Pattern Recognition (61 functions): Candlestick patterns (CDL*)
- Math Transform (15 functions): LN, SQRT, trigonometric functions
- Math Operators (11 functions): MIN, MAX, SUM, etc.

Usage:
    from src.indicators import compute_all_indicators
    from src.data_layer import DataLayer
    
    data_layer = DataLayer()
    ohlcv = data_layer.get_ohlcv("EURUSD", "H1")
    
    indicators = compute_all_indicators(
        ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume
    )
"""

from .overlap_studies import (
    compute_overlap_studies,
    get_overlap_studies_dict,
    OverlapStudiesResult,
    MA_TYPE_SMA, MA_TYPE_EMA, MA_TYPE_WMA, MA_TYPE_DEMA,
    MA_TYPE_TEMA, MA_TYPE_TRIMA, MA_TYPE_KAMA, MA_TYPE_MAMA, MA_TYPE_T3
)

from .momentum import (
    compute_momentum,
    get_momentum_dict,
    MomentumResult
)

from .volume import (
    compute_volume,
    get_volume_dict,
    interpret_volume_indicators,
    VolumeResult
)

from .volatility import (
    compute_volatility,
    get_volatility_dict,
    calculate_atr_stops,
    is_volatility_spike,
    interpret_volatility,
    VolatilityResult
)

from .cycles import (
    compute_cycles,
    get_cycles_dict,
    interpret_cycles,
    get_adaptive_period,
    CycleResult
)

from .price_transform import (
    compute_price_transform,
    get_price_transform_dict,
    analyze_bar_sentiment,
    PriceTransformResult
)

from .statistics import (
    compute_statistics,
    get_statistics_dict,
    interpret_statistics,
    calculate_regression_channel,
    StatisticsResult
)

from .patterns import (
    compute_patterns,
    get_patterns_dict,
    interpret_patterns,
    get_strongest_pattern,
    PatternResult,
    REVERSAL_PATTERNS
)

from .math_transform import (
    compute_math_transform,
    get_math_transform_dict,
    calculate_log_returns,
    MathTransformResult
)

from .math_operators import (
    compute_math_operators,
    get_math_operators_dict,
    find_support_resistance,
    calculate_donchian_channel,
    interpret_price_position,
    MathOperatorsResult
)

import numpy as np
from typing import Dict, Any


def compute_all_indicators(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> Dict[str, Any]:
    """
    Compute ALL 161 indicators across all categories.
    
    This is the main entry point for the Indicator Engine.
    Computes all TA-Lib indicators and returns them organized by category.
    
    Args:
        open_: Open prices (numpy array)
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array)
    
    Returns:
        Dict with all indicators organized by category
    """
    # Compute all categories
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


def get_indicator_count() -> Dict[str, int]:
    """Get count of indicators by category."""
    return {
        "overlap_studies": 18,
        "momentum": 31,
        "volume": 3,
        "volatility": 3,
        "cycles": 5,
        "price_transform": 5,
        "statistics": 9,
        "patterns": 61,
        "math_transform": 15,
        "math_operators": 11,
        "total": 161  # Some functions return multiple values
    }


__all__ = [
    # Main function
    "compute_all_indicators",
    "get_indicator_count",
    
    # Overlap Studies
    "compute_overlap_studies",
    "get_overlap_studies_dict",
    "OverlapStudiesResult",
    "MA_TYPE_SMA", "MA_TYPE_EMA", "MA_TYPE_WMA", "MA_TYPE_DEMA",
    "MA_TYPE_TEMA", "MA_TYPE_TRIMA", "MA_TYPE_KAMA", "MA_TYPE_MAMA", "MA_TYPE_T3",
    
    # Momentum
    "compute_momentum",
    "get_momentum_dict",
    "MomentumResult",
    
    # Volume
    "compute_volume",
    "get_volume_dict",
    "interpret_volume_indicators",
    "VolumeResult",
    
    # Volatility
    "compute_volatility",
    "get_volatility_dict",
    "calculate_atr_stops",
    "is_volatility_spike",
    "interpret_volatility",
    "VolatilityResult",
    
    # Cycles
    "compute_cycles",
    "get_cycles_dict",
    "interpret_cycles",
    "get_adaptive_period",
    "CycleResult",
    
    # Price Transform
    "compute_price_transform",
    "get_price_transform_dict",
    "analyze_bar_sentiment",
    "PriceTransformResult",
    
    # Statistics
    "compute_statistics",
    "get_statistics_dict",
    "interpret_statistics",
    "calculate_regression_channel",
    "StatisticsResult",
    
    # Patterns
    "compute_patterns",
    "get_patterns_dict",
    "interpret_patterns",
    "get_strongest_pattern",
    "PatternResult",
    "REVERSAL_PATTERNS",
    
    # Math Transform
    "compute_math_transform",
    "get_math_transform_dict",
    "calculate_log_returns",
    "MathTransformResult",
    
    # Math Operators
    "compute_math_operators",
    "get_math_operators_dict",
    "find_support_resistance",
    "calculate_donchian_channel",
    "interpret_price_position",
    "MathOperatorsResult",
]
