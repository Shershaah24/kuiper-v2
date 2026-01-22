"""
Kuiper V2 - Volume Indicators (3 Functions)
============================================

All 3 TA-Lib Volume functions with correct input requirements.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
HIGH/LOW/CLOSE/VOLUME:
- AD(high, low, close, volume)
- ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)

CLOSE/VOLUME:
- OBV(close, volume)
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VolumeResult:
    """Container for all volume indicator results."""
    
    # Accumulation/Distribution
    ad: Optional[float] = None
    adosc: Optional[float] = None
    
    # On Balance Volume
    obv: Optional[float] = None
    
    # Full arrays for analysis
    ad_array: Optional[np.ndarray] = None
    obv_array: Optional[np.ndarray] = None


def compute_volume(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> VolumeResult:
    """
    Compute all 3 Volume indicators.
    
    Args:
        open_: Open prices (numpy array) - not used for volume indicators
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array)
    
    Returns:
        VolumeResult with all indicator values
    """
    result = VolumeResult()
    
    if len(close) < 10:
        return result  # Not enough data
    
    # =========================================================================
    # AD - ACCUMULATION/DISTRIBUTION LINE
    # Measures cumulative money flow
    # Formula: AD = Previous AD + CLV * Volume
    # CLV (Close Location Value) = ((Close - Low) - (High - Close)) / (High - Low)
    # 
    # Interpretation:
    #   Rising AD: Accumulation (buying pressure)
    #   Falling AD: Distribution (selling pressure)
    #   AD diverging from price: Potential reversal
    #   AD confirming price: Trend continuation
    # 
    # Key Signals:
    #   - Price making new highs but AD not: Bearish divergence
    #   - Price making new lows but AD not: Bullish divergence
    #   - AD trend direction confirms price trend
    # =========================================================================
    try:
        ad = talib.AD(high, low, close, volume)
        result.ad = _safe_last(ad)
        result.ad_array = ad
    except Exception as e:
        print(f"AD error: {e}")
    
    # =========================================================================
    # ADOSC - CHAIKIN A/D OSCILLATOR
    # MACD applied to Accumulation/Distribution Line
    # Formula: ADOSC = EMA(AD, fast) - EMA(AD, slow)
    # Default: fast=3, slow=10
    # 
    # Interpretation:
    #   > 0: Accumulation momentum increasing
    #   < 0: Distribution momentum increasing
    #   Crossing zero: Shift in money flow
    # 
    # Key Signals:
    #   - ADOSC rising while price falling: Bullish divergence
    #   - ADOSC falling while price rising: Bearish divergence
    #   - Zero line crossovers indicate momentum shifts
    # =========================================================================
    try:
        adosc = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        result.adosc = _safe_last(adosc)
    except Exception as e:
        print(f"ADOSC error: {e}")
    
    # =========================================================================
    # OBV - ON BALANCE VOLUME
    # Cumulative volume indicator
    # Formula:
    #   If Close > Previous Close: OBV = Previous OBV + Volume
    #   If Close < Previous Close: OBV = Previous OBV - Volume
    #   If Close = Previous Close: OBV = Previous OBV
    # 
    # Interpretation:
    #   Rising OBV: Volume flowing into the asset (bullish)
    #   Falling OBV: Volume flowing out of the asset (bearish)
    #   OBV trend more important than absolute value
    # 
    # Key Signals:
    #   - OBV making new highs before price: Bullish (smart money accumulating)
    #   - OBV making new lows before price: Bearish (smart money distributing)
    #   - OBV confirming price breakouts: Strong signal
    #   - OBV diverging from price: Potential reversal
    # =========================================================================
    try:
        obv = talib.OBV(close, volume)
        result.obv = _safe_last(obv)
        result.obv_array = obv
    except Exception as e:
        print(f"OBV error: {e}")
    
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


def get_volume_dict(result: VolumeResult) -> Dict[str, Any]:
    """Convert VolumeResult to dictionary for JSON output."""
    return {
        "AD": result.ad,
        "ADOSC": result.adosc,
        "OBV": result.obv,
    }


def interpret_volume_indicators(result: VolumeResult, price_trend: str) -> Dict[str, str]:
    """
    Interpret volume indicators in context.
    
    Args:
        result: VolumeResult with computed values
        price_trend: "UP", "DOWN", or "SIDEWAYS"
    
    Returns:
        Dict with interpretations for each indicator
    """
    interpretations = {}
    
    # AD interpretation
    if result.ad_array is not None and len(result.ad_array) > 10:
        ad_trend = "rising" if result.ad_array[-1] > result.ad_array[-10] else "falling"
        
        if price_trend == "UP" and ad_trend == "rising":
            interpretations["AD"] = "Accumulation confirms uptrend - healthy buying pressure"
        elif price_trend == "UP" and ad_trend == "falling":
            interpretations["AD"] = "BEARISH DIVERGENCE - Price rising but distribution occurring"
        elif price_trend == "DOWN" and ad_trend == "falling":
            interpretations["AD"] = "Distribution confirms downtrend - selling pressure"
        elif price_trend == "DOWN" and ad_trend == "rising":
            interpretations["AD"] = "BULLISH DIVERGENCE - Price falling but accumulation occurring"
        else:
            interpretations["AD"] = f"AD {ad_trend} in sideways market"
    
    # ADOSC interpretation
    if result.adosc is not None:
        if result.adosc > 0:
            interpretations["ADOSC"] = "Positive - Accumulation momentum increasing"
        else:
            interpretations["ADOSC"] = "Negative - Distribution momentum increasing"
    
    # OBV interpretation
    if result.obv_array is not None and len(result.obv_array) > 10:
        obv_trend = "rising" if result.obv_array[-1] > result.obv_array[-10] else "falling"
        
        if price_trend == "UP" and obv_trend == "rising":
            interpretations["OBV"] = "OBV confirms uptrend - volume supporting price"
        elif price_trend == "UP" and obv_trend == "falling":
            interpretations["OBV"] = "WARNING - Price rising but OBV falling (weak rally)"
        elif price_trend == "DOWN" and obv_trend == "falling":
            interpretations["OBV"] = "OBV confirms downtrend - volume supporting decline"
        elif price_trend == "DOWN" and obv_trend == "rising":
            interpretations["OBV"] = "BULLISH - Price falling but OBV rising (accumulation)"
        else:
            interpretations["OBV"] = f"OBV {obv_trend} in sideways market"
    
    return interpretations
