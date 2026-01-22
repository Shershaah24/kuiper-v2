"""
Kuiper V2 - Volatility Indicators (3 Functions)
================================================

All 3 TA-Lib Volatility functions with correct input requirements.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
HIGH/LOW/CLOSE:
- ATR(high, low, close, timeperiod=14)  # unstable period
- NATR(high, low, close, timeperiod=14)  # unstable period
- TRANGE(high, low, close)
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VolatilityResult:
    """Container for all volatility indicator results."""
    
    # Average True Range
    atr_14: Optional[float] = None
    
    # Normalized ATR (percentage)
    natr_14: Optional[float] = None
    
    # True Range (single bar)
    trange: Optional[float] = None
    
    # Full arrays for analysis
    atr_array: Optional[np.ndarray] = None
    trange_array: Optional[np.ndarray] = None


def compute_volatility(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> VolatilityResult:
    """
    Compute all 3 Volatility indicators.
    
    Args:
        open_: Open prices (numpy array) - not used for volatility indicators
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array) - not used for volatility indicators
    
    Returns:
        VolatilityResult with all indicator values
    """
    result = VolatilityResult()
    
    if len(close) < 14:
        return result  # Not enough data
    
    # =========================================================================
    # TRANGE - TRUE RANGE
    # Measures the true range of price movement for a single bar
    # Formula: TR = Max(High - Low, |High - Previous Close|, |Low - Previous Close|)
    # 
    # The True Range accounts for gaps by comparing:
    #   1. Current bar's range (High - Low)
    #   2. Gap up from previous close (|High - Previous Close|)
    #   3. Gap down from previous close (|Low - Previous Close|)
    # 
    # Interpretation:
    #   High TR: High volatility bar
    #   Low TR: Low volatility bar
    #   TR spikes often occur at trend changes or news events
    # =========================================================================
    try:
        trange = talib.TRANGE(high, low, close)
        result.trange = _safe_last(trange)
        result.trange_array = trange
    except Exception as e:
        print(f"TRANGE error: {e}")
    
    # =========================================================================
    # ATR - AVERAGE TRUE RANGE
    # Smoothed average of True Range over period
    # Formula: ATR = Wilder's Smoothing of TR over period
    # Wilder's Smoothing: ATR = ((Previous ATR * (n-1)) + Current TR) / n
    # 
    # Interpretation:
    #   Rising ATR: Volatility increasing (often at trend starts or reversals)
    #   Falling ATR: Volatility decreasing (consolidation)
    #   ATR spike: Potential trend change or breakout
    # 
    # Key Uses:
    #   - Stop Loss placement: 1.5-2x ATR from entry
    #   - Take Profit targets: 2-3x ATR from entry
    #   - Position sizing: Smaller positions when ATR is high
    #   - Breakout confirmation: Price move > 1x ATR is significant
    # 
    # NOTE: Has unstable period (first ~100 bars may be inaccurate)
    # =========================================================================
    try:
        atr = talib.ATR(high, low, close, timeperiod=14)
        result.atr_14 = _safe_last(atr)
        result.atr_array = atr
    except Exception as e:
        print(f"ATR error: {e}")
    
    # =========================================================================
    # NATR - NORMALIZED AVERAGE TRUE RANGE
    # ATR expressed as percentage of close price
    # Formula: NATR = (ATR / Close) * 100
    # 
    # Advantages over ATR:
    #   - Comparable across different price levels
    #   - Comparable across different instruments
    #   - Useful for comparing volatility of EURUSD vs GBPJPY
    # 
    # Interpretation:
    #   Higher NATR: More volatile relative to price
    #   Lower NATR: Less volatile relative to price
    #   Typical forex NATR: 0.5% - 2.0%
    # 
    # NOTE: Has unstable period
    # =========================================================================
    try:
        natr = talib.NATR(high, low, close, timeperiod=14)
        result.natr_14 = _safe_last(natr)
    except Exception as e:
        print(f"NATR error: {e}")
    
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


def get_volatility_dict(result: VolatilityResult) -> Dict[str, Any]:
    """Convert VolatilityResult to dictionary for JSON output."""
    return {
        "ATR_14": result.atr_14,
        "NATR_14": result.natr_14,
        "TRANGE": result.trange,
    }


def calculate_atr_stops(
    entry_price: float,
    atr: float,
    direction: str,
    sl_multiplier: float = 1.5,
    tp_multiplier: float = 2.5
) -> Dict[str, float]:
    """
    Calculate ATR-based stop loss and take profit levels.
    
    Args:
        entry_price: Entry price for the trade
        atr: Current ATR value
        direction: "LONG" or "SHORT"
        sl_multiplier: ATR multiplier for stop loss (default 1.5)
        tp_multiplier: ATR multiplier for take profit (default 2.5)
    
    Returns:
        Dict with stop_loss, take_profit, and risk_reward_ratio
    """
    if direction == "LONG":
        stop_loss = entry_price - (atr * sl_multiplier)
        take_profit = entry_price + (atr * tp_multiplier)
    else:  # SHORT
        stop_loss = entry_price + (atr * sl_multiplier)
        take_profit = entry_price - (atr * tp_multiplier)
    
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    risk_reward = reward / risk if risk > 0 else 0
    
    return {
        "stop_loss": round(stop_loss, 5),
        "take_profit": round(take_profit, 5),
        "stop_loss_pips": round(atr * sl_multiplier * 10000, 1),  # For forex
        "take_profit_pips": round(atr * tp_multiplier * 10000, 1),
        "risk_reward_ratio": round(risk_reward, 2),
        "atr_value": round(atr, 5)
    }


def is_volatility_spike(result: VolatilityResult, threshold: float = 2.0) -> bool:
    """
    Check if current volatility is spiking (potential regime change).
    
    Args:
        result: VolatilityResult with ATR array
        threshold: Multiple of average ATR to consider a spike (default 2.0)
    
    Returns:
        True if ATR is spiking above threshold
    """
    if result.atr_array is None or len(result.atr_array) < 50:
        return False
    
    # Get average ATR over last 50 bars
    avg_atr = np.nanmean(result.atr_array[-50:-1])
    current_atr = result.atr_14
    
    if avg_atr is None or current_atr is None or avg_atr == 0:
        return False
    
    return current_atr > (avg_atr * threshold)


def interpret_volatility(result: VolatilityResult) -> Dict[str, str]:
    """
    Interpret volatility indicators.
    
    Args:
        result: VolatilityResult with computed values
    
    Returns:
        Dict with interpretations
    """
    interpretations = {}
    
    # ATR interpretation
    if result.atr_array is not None and len(result.atr_array) > 20:
        recent_avg = np.nanmean(result.atr_array[-20:])
        older_avg = np.nanmean(result.atr_array[-50:-20]) if len(result.atr_array) > 50 else recent_avg
        
        if recent_avg > older_avg * 1.3:
            interpretations["ATR"] = "Volatility EXPANDING - Potential trend start or reversal"
        elif recent_avg < older_avg * 0.7:
            interpretations["ATR"] = "Volatility CONTRACTING - Consolidation, breakout may follow"
        else:
            interpretations["ATR"] = "Volatility STABLE - Normal market conditions"
    
    # NATR interpretation
    if result.natr_14 is not None:
        if result.natr_14 > 1.5:
            interpretations["NATR"] = f"HIGH volatility ({result.natr_14:.2f}%) - Use wider stops, smaller position"
        elif result.natr_14 < 0.5:
            interpretations["NATR"] = f"LOW volatility ({result.natr_14:.2f}%) - Tight range, breakout potential"
        else:
            interpretations["NATR"] = f"NORMAL volatility ({result.natr_14:.2f}%)"
    
    # Spike check
    if is_volatility_spike(result):
        interpretations["SPIKE"] = "VOLATILITY SPIKE DETECTED - Exercise caution, potential regime change"
    
    return interpretations
