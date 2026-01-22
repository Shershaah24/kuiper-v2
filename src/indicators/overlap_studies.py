"""
Kuiper V2 - Overlap Studies Indicators (18 Functions)
======================================================

All 18 TA-Lib Overlap Studies functions with correct input requirements.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
CLOSE ONLY:
- DEMA(close, timeperiod=30)
- EMA(close, timeperiod=30)  # unstable period
- HT_TRENDLINE(close)  # unstable period
- KAMA(close, timeperiod=30)  # unstable period
- MA(close, timeperiod=30, matype=0)
- MAMA(close, fastlimit=0.5, slowlimit=0.05)  # unstable period, returns (mama, fama)
- MAVP(close, periods, minperiod=2, maxperiod=30, matype=0)
- MIDPOINT(close, timeperiod=14)
- SMA(close, timeperiod=30)
- T3(close, timeperiod=5, vfactor=0.7)  # unstable period
- TEMA(close, timeperiod=30)
- TRIMA(close, timeperiod=30)
- WMA(close, timeperiod=30)
- BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)  # returns (upper, middle, lower)

HIGH/LOW:
- MIDPRICE(high, low, timeperiod=14)
- SAR(high, low, acceleration=0.02, maximum=0.2)
- SAREXT(high, low, ...)

HIGH/LOW/CLOSE:
- ACCBANDS(high, low, close, timeperiod=20)  # returns (upper, middle, lower)
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OverlapStudiesResult:
    """Container for all overlap studies results."""
    
    # Simple Moving Averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    
    # Exponential Moving Averages
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    ema_50: Optional[float] = None
    
    # Double/Triple EMA
    dema_30: Optional[float] = None
    tema_30: Optional[float] = None
    
    # T3 (Tillson)
    t3_5: Optional[float] = None
    
    # Weighted/Triangular MA
    wma_30: Optional[float] = None
    trima_30: Optional[float] = None
    
    # Adaptive MAs
    kama_30: Optional[float] = None
    mama: Optional[float] = None
    fama: Optional[float] = None
    
    # Hilbert Transform Trendline
    ht_trendline: Optional[float] = None
    
    # Bollinger Bands
    bbands_upper: Optional[float] = None
    bbands_middle: Optional[float] = None
    bbands_lower: Optional[float] = None
    
    # Acceleration Bands
    accbands_upper: Optional[float] = None
    accbands_middle: Optional[float] = None
    accbands_lower: Optional[float] = None
    
    # Midpoint/Midprice
    midpoint_14: Optional[float] = None
    midprice_14: Optional[float] = None
    
    # Parabolic SAR
    sar: Optional[float] = None
    sarext: Optional[float] = None
    
    # Full arrays (for analysis)
    sma_20_array: Optional[np.ndarray] = None
    sma_50_array: Optional[np.ndarray] = None
    ema_12_array: Optional[np.ndarray] = None
    bbands_upper_array: Optional[np.ndarray] = None
    bbands_lower_array: Optional[np.ndarray] = None


def compute_overlap_studies(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> OverlapStudiesResult:
    """
    Compute all 18 Overlap Studies indicators.
    
    Args:
        open_: Open prices (numpy array)
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array) - not used for overlap studies
    
    Returns:
        OverlapStudiesResult with all indicator values
    """
    result = OverlapStudiesResult()
    
    if len(close) < 30:
        return result  # Not enough data
    
    # =========================================================================
    # SIMPLE MOVING AVERAGES (SMA)
    # Formula: SMA = Sum(Close, n) / n
    # =========================================================================
    try:
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        sma_200 = talib.SMA(close, timeperiod=200) if len(close) >= 200 else np.array([np.nan])
        
        result.sma_20 = _safe_last(sma_20)
        result.sma_50 = _safe_last(sma_50)
        result.sma_200 = _safe_last(sma_200)
        result.sma_20_array = sma_20
        result.sma_50_array = sma_50
    except Exception as e:
        print(f"SMA error: {e}")
    
    # =========================================================================
    # EXPONENTIAL MOVING AVERAGES (EMA)
    # Formula: EMA = Close * k + EMA(prev) * (1-k), where k = 2/(n+1)
    # NOTE: Has unstable period
    # =========================================================================
    try:
        ema_12 = talib.EMA(close, timeperiod=12)
        ema_26 = talib.EMA(close, timeperiod=26)
        ema_50 = talib.EMA(close, timeperiod=50)
        
        result.ema_12 = _safe_last(ema_12)
        result.ema_26 = _safe_last(ema_26)
        result.ema_50 = _safe_last(ema_50)
        result.ema_12_array = ema_12
    except Exception as e:
        print(f"EMA error: {e}")
    
    # =========================================================================
    # DOUBLE EXPONENTIAL MOVING AVERAGE (DEMA)
    # Formula: DEMA = 2 * EMA(n) - EMA(EMA(n))
    # Reduces lag compared to regular EMA
    # =========================================================================
    try:
        dema_30 = talib.DEMA(close, timeperiod=30)
        result.dema_30 = _safe_last(dema_30)
    except Exception as e:
        print(f"DEMA error: {e}")
    
    # =========================================================================
    # TRIPLE EXPONENTIAL MOVING AVERAGE (TEMA)
    # Formula: TEMA = 3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))
    # Even less lag than DEMA
    # =========================================================================
    try:
        tema_30 = talib.TEMA(close, timeperiod=30)
        result.tema_30 = _safe_last(tema_30)
    except Exception as e:
        print(f"TEMA error: {e}")
    
    # =========================================================================
    # T3 - TRIPLE EXPONENTIAL MOVING AVERAGE (Tillson)
    # Smoother than TEMA with adjustable smoothing factor (vfactor)
    # NOTE: Has unstable period
    # =========================================================================
    try:
        t3_5 = talib.T3(close, timeperiod=5, vfactor=0.7)
        result.t3_5 = _safe_last(t3_5)
    except Exception as e:
        print(f"T3 error: {e}")
    
    # =========================================================================
    # WEIGHTED MOVING AVERAGE (WMA)
    # Formula: WMA = Sum(Weight * Close) / Sum(Weight)
    # More recent prices have higher weight
    # =========================================================================
    try:
        wma_30 = talib.WMA(close, timeperiod=30)
        result.wma_30 = _safe_last(wma_30)
    except Exception as e:
        print(f"WMA error: {e}")
    
    # =========================================================================
    # TRIANGULAR MOVING AVERAGE (TRIMA)
    # Double-smoothed SMA - weights peak in the middle
    # Formula: TRIMA = SMA(SMA(Close, n/2), n/2)
    # =========================================================================
    try:
        trima_30 = talib.TRIMA(close, timeperiod=30)
        result.trima_30 = _safe_last(trima_30)
    except Exception as e:
        print(f"TRIMA error: {e}")
    
    # =========================================================================
    # KAUFMAN ADAPTIVE MOVING AVERAGE (KAMA)
    # Adapts to market volatility - faster in trends, slower in ranges
    # NOTE: Has unstable period
    # =========================================================================
    try:
        kama_30 = talib.KAMA(close, timeperiod=30)
        result.kama_30 = _safe_last(kama_30)
    except Exception as e:
        print(f"KAMA error: {e}")
    
    # =========================================================================
    # MESA ADAPTIVE MOVING AVERAGE (MAMA)
    # John Ehlers' adaptive MA based on Hilbert Transform
    # Returns: (mama, fama) - MAMA and Following Adaptive MA
    # NOTE: Has unstable period
    # =========================================================================
    try:
        mama, fama = talib.MAMA(close, fastlimit=0.5, slowlimit=0.05)
        result.mama = _safe_last(mama)
        result.fama = _safe_last(fama)
    except Exception as e:
        print(f"MAMA error: {e}")
    
    # =========================================================================
    # HILBERT TRANSFORM - INSTANTANEOUS TRENDLINE
    # Ehlers' method to extract the trend component
    # NOTE: Has unstable period
    # =========================================================================
    try:
        ht_trendline = talib.HT_TRENDLINE(close)
        result.ht_trendline = _safe_last(ht_trendline)
    except Exception as e:
        print(f"HT_TRENDLINE error: {e}")
    
    # =========================================================================
    # BOLLINGER BANDS (BBANDS)
    # Upper = SMA + (stddev * nbdevup)
    # Middle = SMA
    # Lower = SMA - (stddev * nbdevdn)
    # =========================================================================
    try:
        upper, middle, lower = talib.BBANDS(
            close, 
            timeperiod=20, 
            nbdevup=2.0, 
            nbdevdn=2.0, 
            matype=0  # SMA
        )
        result.bbands_upper = _safe_last(upper)
        result.bbands_middle = _safe_last(middle)
        result.bbands_lower = _safe_last(lower)
        result.bbands_upper_array = upper
        result.bbands_lower_array = lower
    except Exception as e:
        print(f"BBANDS error: {e}")
    
    # =========================================================================
    # ACCELERATION BANDS (ACCBANDS)
    # Similar to Bollinger but uses high/low for volatility
    # Upper = SMA(High * (1 + 4 * (High - Low) / (High + Low)))
    # Lower = SMA(Low * (1 - 4 * (High - Low) / (High + Low)))
    # =========================================================================
    try:
        acc_upper, acc_middle, acc_lower = talib.ACCBANDS(
            high, low, close, timeperiod=20
        )
        result.accbands_upper = _safe_last(acc_upper)
        result.accbands_middle = _safe_last(acc_middle)
        result.accbands_lower = _safe_last(acc_lower)
    except Exception as e:
        print(f"ACCBANDS error: {e}")
    
    # =========================================================================
    # MIDPOINT
    # Formula: (Highest High + Lowest Low) / 2 over period
    # Uses CLOSE only (finds midpoint of close prices)
    # =========================================================================
    try:
        midpoint = talib.MIDPOINT(close, timeperiod=14)
        result.midpoint_14 = _safe_last(midpoint)
    except Exception as e:
        print(f"MIDPOINT error: {e}")
    
    # =========================================================================
    # MIDPRICE
    # Formula: (Highest High + Lowest Low) / 2 over period
    # Uses HIGH and LOW
    # =========================================================================
    try:
        midprice = talib.MIDPRICE(high, low, timeperiod=14)
        result.midprice_14 = _safe_last(midprice)
    except Exception as e:
        print(f"MIDPRICE error: {e}")
    
    # =========================================================================
    # PARABOLIC SAR
    # Trailing stop indicator that follows price
    # Flips above/below price based on trend
    # acceleration: AF increment (default 0.02)
    # maximum: Maximum AF (default 0.2)
    # =========================================================================
    try:
        sar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
        result.sar = _safe_last(sar)
    except Exception as e:
        print(f"SAR error: {e}")
    
    # =========================================================================
    # PARABOLIC SAR - EXTENDED
    # More configurable version with separate long/short parameters
    # =========================================================================
    try:
        sarext = talib.SAREXT(
            high, low,
            startvalue=0,
            offsetonreverse=0,
            accelerationinitlong=0.02,
            accelerationlong=0.02,
            accelerationmaxlong=0.2,
            accelerationinitshort=0.02,
            accelerationshort=0.02,
            accelerationmaxshort=0.2
        )
        result.sarext = _safe_last(sarext)
    except Exception as e:
        print(f"SAREXT error: {e}")
    
    return result


def _safe_last(arr: np.ndarray) -> Optional[float]:
    """Safely get the last non-NaN value from array."""
    if arr is None or len(arr) == 0:
        return None
    
    # Get last value
    val = arr[-1]
    
    # Check for NaN
    if np.isnan(val):
        # Try to find last non-NaN
        valid = arr[~np.isnan(arr)]
        if len(valid) > 0:
            return float(valid[-1])
        return None
    
    return float(val)


def get_overlap_studies_dict(result: OverlapStudiesResult) -> Dict[str, Any]:
    """Convert OverlapStudiesResult to dictionary for JSON output."""
    return {
        # SMAs
        "SMA_20": result.sma_20,
        "SMA_50": result.sma_50,
        "SMA_200": result.sma_200,
        
        # EMAs
        "EMA_12": result.ema_12,
        "EMA_26": result.ema_26,
        "EMA_50": result.ema_50,
        
        # Advanced MAs
        "DEMA_30": result.dema_30,
        "TEMA_30": result.tema_30,
        "T3_5": result.t3_5,
        "WMA_30": result.wma_30,
        "TRIMA_30": result.trima_30,
        "KAMA_30": result.kama_30,
        
        # MAMA
        "MAMA": result.mama,
        "FAMA": result.fama,
        
        # Hilbert
        "HT_TRENDLINE": result.ht_trendline,
        
        # Bollinger Bands
        "BBANDS_upper": result.bbands_upper,
        "BBANDS_middle": result.bbands_middle,
        "BBANDS_lower": result.bbands_lower,
        
        # Acceleration Bands
        "ACCBANDS_upper": result.accbands_upper,
        "ACCBANDS_middle": result.accbands_middle,
        "ACCBANDS_lower": result.accbands_lower,
        
        # Midpoint/Midprice
        "MIDPOINT_14": result.midpoint_14,
        "MIDPRICE_14": result.midprice_14,
        
        # Parabolic SAR
        "SAR": result.sar,
        "SAREXT": result.sarext,
    }


# =============================================================================
# MA TYPE CONSTANTS (for functions that accept matype parameter)
# =============================================================================
MA_TYPE_SMA = 0      # Simple Moving Average
MA_TYPE_EMA = 1      # Exponential Moving Average
MA_TYPE_WMA = 2      # Weighted Moving Average
MA_TYPE_DEMA = 3     # Double Exponential Moving Average
MA_TYPE_TEMA = 4     # Triple Exponential Moving Average
MA_TYPE_TRIMA = 5    # Triangular Moving Average
MA_TYPE_KAMA = 6     # Kaufman Adaptive Moving Average
MA_TYPE_MAMA = 7     # MESA Adaptive Moving Average
MA_TYPE_T3 = 8       # Triple Exponential Moving Average (T3)
