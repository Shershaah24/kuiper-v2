"""
Kuiper V2 - Math Operators (11 Functions)
==========================================

All 11 TA-Lib Math Operator functions.
These perform mathematical operations on price data.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
TWO ARRAYS:
- ADD(high, low)    # Vector Addition
- DIV(high, low)    # Vector Division
- MULT(high, low)   # Vector Multiplication
- SUB(high, low)    # Vector Subtraction

SINGLE ARRAY WITH PERIOD:
- MAX(close, timeperiod=30)       # Highest value over period
- MAXINDEX(close, timeperiod=30)  # Index of highest value
- MIN(close, timeperiod=30)       # Lowest value over period
- MININDEX(close, timeperiod=30)  # Index of lowest value
- MINMAX(close, timeperiod=30)    # Returns (min, max)
- MINMAXINDEX(close, timeperiod=30)  # Returns (minidx, maxidx)
- SUM(close, timeperiod=30)       # Sum over period
"""

import numpy as np
import talib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MathOperatorsResult:
    """Container for math operator results."""
    
    # Min/Max values
    max_30: Optional[float] = None
    min_30: Optional[float] = None
    max_index_30: Optional[int] = None
    min_index_30: Optional[int] = None
    
    # Sum
    sum_30: Optional[float] = None
    
    # Range calculations (high - low)
    range_current: Optional[float] = None
    
    # Full arrays for analysis
    max_array: Optional[np.ndarray] = None
    min_array: Optional[np.ndarray] = None


def compute_math_operators(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> MathOperatorsResult:
    """
    Compute all 11 Math Operator functions.
    
    These are useful for:
    - Finding support/resistance (MIN/MAX)
    - Calculating ranges (SUB)
    - Summing values (SUM)
    
    Args:
        open_: Open prices
        high: High prices
        low: Low prices
        close: Close prices
        volume: Volume
    
    Returns:
        MathOperatorsResult with all values
    """
    result = MathOperatorsResult()
    
    if len(close) < 30:
        return result
    
    # =========================================================================
    # MAX - HIGHEST VALUE OVER PERIOD
    # Useful for finding resistance levels
    # =========================================================================
    try:
        max_vals = talib.MAX(close, timeperiod=30)
        result.max_30 = _safe_last(max_vals)
        result.max_array = max_vals
    except Exception as e:
        pass
    
    # =========================================================================
    # MIN - LOWEST VALUE OVER PERIOD
    # Useful for finding support levels
    # =========================================================================
    try:
        min_vals = talib.MIN(close, timeperiod=30)
        result.min_30 = _safe_last(min_vals)
        result.min_array = min_vals
    except Exception as e:
        pass
    
    # =========================================================================
    # MAXINDEX - INDEX OF HIGHEST VALUE
    # Shows how many bars ago the high was made
    # =========================================================================
    try:
        max_idx = talib.MAXINDEX(close, timeperiod=30)
        result.max_index_30 = int(_safe_last(max_idx)) if _safe_last(max_idx) is not None else None
    except Exception as e:
        pass
    
    # =========================================================================
    # MININDEX - INDEX OF LOWEST VALUE
    # Shows how many bars ago the low was made
    # =========================================================================
    try:
        min_idx = talib.MININDEX(close, timeperiod=30)
        result.min_index_30 = int(_safe_last(min_idx)) if _safe_last(min_idx) is not None else None
    except Exception as e:
        pass
    
    # =========================================================================
    # SUM - SUM OVER PERIOD
    # Useful for cumulative calculations
    # =========================================================================
    try:
        sum_vals = talib.SUM(close, timeperiod=30)
        result.sum_30 = _safe_last(sum_vals)
    except Exception as e:
        pass
    
    # =========================================================================
    # RANGE CALCULATION (using SUB)
    # Current bar's range = High - Low
    # =========================================================================
    try:
        range_vals = talib.SUB(high, low)
        result.range_current = _safe_last(range_vals)
    except Exception as e:
        pass
    
    return result


def _safe_last(arr: np.ndarray) -> Optional[float]:
    """Safely get the last non-NaN value from array."""
    if arr is None or len(arr) == 0:
        return None
    
    val = arr[-1]
    
    if np.isnan(val):
        valid = arr[~np.isnan(arr)]
        if len(valid) > 0:
            return float(valid[-1])
        return None
    
    return float(val)


def get_math_operators_dict(result: MathOperatorsResult) -> Dict[str, Any]:
    """Convert MathOperatorsResult to dictionary for JSON output."""
    return {
        "MAX_30": result.max_30,
        "MIN_30": result.min_30,
        "MAX_INDEX_30": result.max_index_30,
        "MIN_INDEX_30": result.min_index_30,
        "SUM_30": result.sum_30,
        "RANGE_CURRENT": result.range_current,
    }


def find_support_resistance(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    period: int = 30
) -> Dict[str, float]:
    """
    Find support and resistance levels using MIN/MAX.
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Lookback period
    
    Returns:
        Dict with support, resistance, and current position
    """
    if len(close) < period:
        return {"support": None, "resistance": None, "position": None}
    
    # Resistance from highs
    resistance = talib.MAX(high, timeperiod=period)
    resistance_level = _safe_last(resistance)
    
    # Support from lows
    support = talib.MIN(low, timeperiod=period)
    support_level = _safe_last(support)
    
    # Current price position in range
    current_price = close[-1]
    
    if resistance_level and support_level and resistance_level != support_level:
        range_size = resistance_level - support_level
        position = (current_price - support_level) / range_size
    else:
        position = 0.5
    
    return {
        "support": round(support_level, 5) if support_level else None,
        "resistance": round(resistance_level, 5) if resistance_level else None,
        "range": round(resistance_level - support_level, 5) if resistance_level and support_level else None,
        "position_in_range": round(position, 2),  # 0 = at support, 1 = at resistance
        "near_support": position < 0.2,
        "near_resistance": position > 0.8,
    }


def calculate_donchian_channel(
    high: np.ndarray,
    low: np.ndarray,
    period: int = 20
) -> Dict[str, float]:
    """
    Calculate Donchian Channel using MAX/MIN.
    
    Donchian Channel:
    - Upper = Highest High over period
    - Lower = Lowest Low over period
    - Middle = (Upper + Lower) / 2
    
    Args:
        high: High prices
        low: Low prices
        period: Channel period
    
    Returns:
        Dict with upper, middle, lower channel values
    """
    if len(high) < period:
        return {"upper": None, "middle": None, "lower": None}
    
    upper = talib.MAX(high, timeperiod=period)
    lower = talib.MIN(low, timeperiod=period)
    
    upper_val = _safe_last(upper)
    lower_val = _safe_last(lower)
    
    if upper_val and lower_val:
        middle_val = (upper_val + lower_val) / 2
    else:
        middle_val = None
    
    return {
        "upper": round(upper_val, 5) if upper_val else None,
        "middle": round(middle_val, 5) if middle_val else None,
        "lower": round(lower_val, 5) if lower_val else None,
        "width": round(upper_val - lower_val, 5) if upper_val and lower_val else None,
    }


def interpret_price_position(result: MathOperatorsResult, current_price: float) -> Dict[str, str]:
    """
    Interpret current price position relative to recent range.
    
    Args:
        result: MathOperatorsResult with MIN/MAX values
        current_price: Current close price
    
    Returns:
        Dict with interpretations
    """
    interpretations = {}
    
    if result.max_30 and result.min_30:
        range_size = result.max_30 - result.min_30
        
        if range_size > 0:
            position = (current_price - result.min_30) / range_size
            
            if position > 0.9:
                interpretations["position"] = "At 30-bar HIGH - Potential resistance"
            elif position > 0.7:
                interpretations["position"] = "Upper range - Approaching resistance"
            elif position < 0.1:
                interpretations["position"] = "At 30-bar LOW - Potential support"
            elif position < 0.3:
                interpretations["position"] = "Lower range - Approaching support"
            else:
                interpretations["position"] = "Mid-range"
    
    # How recent was the high/low?
    if result.max_index_30 is not None:
        bars_since_high = 30 - result.max_index_30
        if bars_since_high <= 3:
            interpretations["high_recency"] = f"NEW HIGH made {bars_since_high} bars ago"
        elif bars_since_high >= 25:
            interpretations["high_recency"] = f"High was {bars_since_high} bars ago - aging"
    
    if result.min_index_30 is not None:
        bars_since_low = 30 - result.min_index_30
        if bars_since_low <= 3:
            interpretations["low_recency"] = f"NEW LOW made {bars_since_low} bars ago"
        elif bars_since_low >= 25:
            interpretations["low_recency"] = f"Low was {bars_since_low} bars ago - aging"
    
    return interpretations
