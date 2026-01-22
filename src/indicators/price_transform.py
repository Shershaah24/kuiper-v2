"""
Kuiper V2 - Price Transform Indicators (5 Functions)
=====================================================

All 5 TA-Lib Price Transform functions.
These create derived price series used by other indicators.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
CLOSE ONLY:
- AVGDEV(close, timeperiod=14)  # Average Deviation

OPEN/HIGH/LOW/CLOSE:
- AVGPRICE(open, high, low, close)  # Average Price

HIGH/LOW:
- MEDPRICE(high, low)  # Median Price

HIGH/LOW/CLOSE:
- TYPPRICE(high, low, close)  # Typical Price
- WCLPRICE(high, low, close)  # Weighted Close Price
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PriceTransformResult:
    """Container for all price transform results."""
    
    # Average Deviation
    avgdev_14: Optional[float] = None
    
    # Average Price
    avgprice: Optional[float] = None
    
    # Median Price
    medprice: Optional[float] = None
    
    # Typical Price
    typprice: Optional[float] = None
    
    # Weighted Close Price
    wclprice: Optional[float] = None
    
    # Full arrays for analysis
    typprice_array: Optional[np.ndarray] = None


def compute_price_transform(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> PriceTransformResult:
    """
    Compute all 5 Price Transform indicators.
    
    These create alternative price representations:
    - AVGPRICE: Simple average of OHLC
    - MEDPRICE: Midpoint of High-Low range
    - TYPPRICE: Most commonly used (HLC/3)
    - WCLPRICE: Emphasizes close price
    - AVGDEV: Measures price dispersion
    
    Args:
        open_: Open prices (numpy array)
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array) - not used
    
    Returns:
        PriceTransformResult with all values
    """
    result = PriceTransformResult()
    
    if len(close) < 14:
        return result
    
    # =========================================================================
    # AVGPRICE - AVERAGE PRICE
    # Simple average of all four OHLC prices
    # Formula: AVGPRICE = (Open + High + Low + Close) / 4
    # 
    # Interpretation:
    #   Represents the "average" price of the bar
    #   Smooths out the emphasis on any single price point
    #   Less commonly used than Typical Price
    # 
    # Use Cases:
    #   - Alternative price input for indicators
    #   - Comparing to close to gauge bar sentiment
    #   - Close > AVGPRICE: Bullish bar
    #   - Close < AVGPRICE: Bearish bar
    # =========================================================================
    try:
        avgprice = talib.AVGPRICE(open_, high, low, close)
        result.avgprice = _safe_last(avgprice)
    except Exception as e:
        print(f"AVGPRICE error: {e}")
    
    # =========================================================================
    # MEDPRICE - MEDIAN PRICE
    # Midpoint of the High-Low range
    # Formula: MEDPRICE = (High + Low) / 2
    # 
    # Interpretation:
    #   Represents the center of the bar's range
    #   Ignores open and close
    #   Good for measuring "fair value" of the bar
    # 
    # Use Cases:
    #   - Input for some indicators (like CCI uses Typical Price)
    #   - Pivot point calculations
    #   - Close > MEDPRICE: Closed in upper half of range (bullish)
    #   - Close < MEDPRICE: Closed in lower half of range (bearish)
    # =========================================================================
    try:
        medprice = talib.MEDPRICE(high, low)
        result.medprice = _safe_last(medprice)
    except Exception as e:
        print(f"MEDPRICE error: {e}")
    
    # =========================================================================
    # TYPPRICE - TYPICAL PRICE
    # Average of High, Low, and Close
    # Formula: TYPPRICE = (High + Low + Close) / 3
    # 
    # This is the MOST COMMONLY USED price transform because:
    #   - Includes the close (most important price)
    #   - Includes the range (high/low)
    #   - Used by CCI, MFI, and many other indicators
    # 
    # Interpretation:
    #   Represents a "typical" or "representative" price
    #   Better than just close for range-based analysis
    # 
    # Use Cases:
    #   - Input for CCI calculation
    #   - Input for MFI calculation
    #   - Volume-weighted average price calculations
    #   - Support/resistance level calculations
    # =========================================================================
    try:
        typprice = talib.TYPPRICE(high, low, close)
        result.typprice = _safe_last(typprice)
        result.typprice_array = typprice
    except Exception as e:
        print(f"TYPPRICE error: {e}")
    
    # =========================================================================
    # WCLPRICE - WEIGHTED CLOSE PRICE
    # Close-weighted average emphasizing the close
    # Formula: WCLPRICE = (High + Low + Close + Close) / 4
    #        = (High + Low + 2*Close) / 4
    # 
    # Interpretation:
    #   Gives double weight to the close price
    #   Close is considered most important (settlement price)
    #   More responsive to close than Typical Price
    # 
    # Use Cases:
    #   - When close price is most important
    #   - Alternative to Typical Price
    #   - Some pivot point calculations
    # =========================================================================
    try:
        wclprice = talib.WCLPRICE(high, low, close)
        result.wclprice = _safe_last(wclprice)
    except Exception as e:
        print(f"WCLPRICE error: {e}")
    
    # =========================================================================
    # AVGDEV - AVERAGE DEVIATION
    # Mean absolute deviation from the mean
    # Formula: AVGDEV = SUM(|Close - SMA(Close)|) / n
    # 
    # Interpretation:
    #   Measures how much prices deviate from average
    #   Similar to standard deviation but uses absolute values
    #   Higher AVGDEV = More price dispersion = More volatility
    # 
    # Use Cases:
    #   - Volatility measurement
    #   - Alternative to ATR for volatility
    #   - Detecting consolidation (low AVGDEV)
    #   - Detecting breakouts (rising AVGDEV)
    # =========================================================================
    try:
        avgdev = talib.AVGDEV(close, timeperiod=14)
        result.avgdev_14 = _safe_last(avgdev)
    except Exception as e:
        print(f"AVGDEV error: {e}")
    
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


def get_price_transform_dict(result: PriceTransformResult) -> Dict[str, Any]:
    """Convert PriceTransformResult to dictionary for JSON output."""
    return {
        "AVGDEV_14": result.avgdev_14,
        "AVGPRICE": result.avgprice,
        "MEDPRICE": result.medprice,
        "TYPPRICE": result.typprice,
        "WCLPRICE": result.wclprice,
    }


def analyze_bar_sentiment(
    open_: float,
    high: float,
    low: float,
    close: float
) -> Dict[str, Any]:
    """
    Analyze single bar sentiment using price transforms.
    
    Args:
        open_: Open price
        high: High price
        low: Low price
        close: Close price
    
    Returns:
        Dict with bar analysis
    """
    # Calculate transforms
    avgprice = (open_ + high + low + close) / 4
    medprice = (high + low) / 2
    typprice = (high + low + close) / 3
    wclprice = (high + low + 2 * close) / 4
    
    # Bar range
    bar_range = high - low
    
    # Close position in range (0 = low, 1 = high)
    close_position = (close - low) / bar_range if bar_range > 0 else 0.5
    
    # Sentiment analysis
    sentiment = "NEUTRAL"
    if close_position > 0.7:
        sentiment = "BULLISH"
    elif close_position < 0.3:
        sentiment = "BEARISH"
    
    # Body analysis
    body = abs(close - open_)
    body_ratio = body / bar_range if bar_range > 0 else 0
    
    bar_type = "DOJI"
    if body_ratio > 0.6:
        bar_type = "STRONG_BODY"
    elif body_ratio > 0.3:
        bar_type = "NORMAL_BODY"
    
    return {
        "avgprice": round(avgprice, 5),
        "medprice": round(medprice, 5),
        "typprice": round(typprice, 5),
        "wclprice": round(wclprice, 5),
        "close_position": round(close_position, 2),
        "sentiment": sentiment,
        "bar_type": bar_type,
        "body_ratio": round(body_ratio, 2),
        "close_vs_avgprice": "ABOVE" if close > avgprice else "BELOW",
        "close_vs_medprice": "ABOVE" if close > medprice else "BELOW",
    }
