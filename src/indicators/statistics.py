"""
Kuiper V2 - Statistical Functions (9 Functions)
================================================

All 9 TA-Lib Statistical functions for regression and variance analysis.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
CLOSE ONLY:
- LINEARREG(close, timeperiod=14)           # Linear Regression
- LINEARREG_ANGLE(close, timeperiod=14)     # Linear Regression Angle
- LINEARREG_INTERCEPT(close, timeperiod=14) # Linear Regression Intercept
- LINEARREG_SLOPE(close, timeperiod=14)     # Linear Regression Slope
- STDDEV(close, timeperiod=5, nbdev=1)      # Standard Deviation
- TSF(close, timeperiod=14)                 # Time Series Forecast
- VAR(close, timeperiod=5, nbdev=1)         # Variance

TWO ARRAYS (HIGH/LOW used as example):
- BETA(high, low, timeperiod=5)             # Beta coefficient
- CORREL(high, low, timeperiod=30)          # Pearson Correlation
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class StatisticsResult:
    """Container for all statistical function results."""
    
    # Linear Regression
    linearreg_14: Optional[float] = None
    linearreg_angle_14: Optional[float] = None
    linearreg_intercept_14: Optional[float] = None
    linearreg_slope_14: Optional[float] = None
    
    # Standard Deviation and Variance
    stddev_5: Optional[float] = None
    var_5: Optional[float] = None
    
    # Time Series Forecast
    tsf_14: Optional[float] = None
    
    # Beta and Correlation (high vs low)
    beta_5: Optional[float] = None
    correl_30: Optional[float] = None
    
    # Full arrays for analysis
    linearreg_array: Optional[np.ndarray] = None
    stddev_array: Optional[np.ndarray] = None


def compute_statistics(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> StatisticsResult:
    """
    Compute all 9 Statistical functions.
    
    These provide regression analysis and statistical measures:
    - Linear regression for trend analysis
    - Standard deviation for volatility
    - Beta and correlation for relationship analysis
    
    Args:
        open_: Open prices (numpy array) - not used
        high: High prices (numpy array) - used for BETA/CORREL
        low: Low prices (numpy array) - used for BETA/CORREL
        close: Close prices (numpy array)
        volume: Volume (numpy array) - not used
    
    Returns:
        StatisticsResult with all values
    """
    result = StatisticsResult()
    
    if len(close) < 30:
        return result
    
    # =========================================================================
    # LINEARREG - LINEAR REGRESSION
    # Fits a straight line to price data using least squares
    # Returns the endpoint of the regression line
    # 
    # Formula: y = mx + b (returns y at current bar)
    # 
    # Interpretation:
    #   Price > LINEARREG: Price above trend (potentially overbought)
    #   Price < LINEARREG: Price below trend (potentially oversold)
    #   LINEARREG acts like a smoothed moving average
    # 
    # Use Cases:
    #   - Trend identification
    #   - Dynamic support/resistance
    #   - Mean reversion signals when price deviates
    # =========================================================================
    try:
        linearreg = talib.LINEARREG(close, timeperiod=14)
        result.linearreg_14 = _safe_last(linearreg)
        result.linearreg_array = linearreg
    except Exception as e:
        print(f"LINEARREG error: {e}")
    
    # =========================================================================
    # LINEARREG_ANGLE - LINEAR REGRESSION ANGLE
    # Angle of the regression line in degrees
    # 
    # Formula: angle = arctan(slope) * (180/π)
    # 
    # Interpretation:
    #   > 0: Upward trend
    #   < 0: Downward trend
    #   Near 0: Flat/sideways
    #   Steeper angle: Stronger trend
    # 
    # Typical ranges:
    #   Strong trend: |angle| > 45°
    #   Moderate trend: 20° < |angle| < 45°
    #   Weak/no trend: |angle| < 20°
    # =========================================================================
    try:
        linearreg_angle = talib.LINEARREG_ANGLE(close, timeperiod=14)
        result.linearreg_angle_14 = _safe_last(linearreg_angle)
    except Exception as e:
        print(f"LINEARREG_ANGLE error: {e}")
    
    # =========================================================================
    # LINEARREG_INTERCEPT - LINEAR REGRESSION INTERCEPT
    # Y-intercept of the regression line
    # 
    # Formula: b in y = mx + b
    # 
    # Less commonly used directly, but useful for:
    #   - Projecting price levels
    #   - Calculating regression channels
    # =========================================================================
    try:
        linearreg_intercept = talib.LINEARREG_INTERCEPT(close, timeperiod=14)
        result.linearreg_intercept_14 = _safe_last(linearreg_intercept)
    except Exception as e:
        print(f"LINEARREG_INTERCEPT error: {e}")
    
    # =========================================================================
    # LINEARREG_SLOPE - LINEAR REGRESSION SLOPE
    # Slope of the regression line (rate of change)
    # 
    # Formula: m in y = mx + b
    # 
    # Interpretation:
    #   > 0: Price trending up
    #   < 0: Price trending down
    #   = 0: No trend
    #   Magnitude indicates trend strength
    # 
    # Use Cases:
    #   - Trend direction confirmation
    #   - Comparing trend strength across timeframes
    #   - Detecting trend acceleration/deceleration
    # =========================================================================
    try:
        linearreg_slope = talib.LINEARREG_SLOPE(close, timeperiod=14)
        result.linearreg_slope_14 = _safe_last(linearreg_slope)
    except Exception as e:
        print(f"LINEARREG_SLOPE error: {e}")
    
    # =========================================================================
    # STDDEV - STANDARD DEVIATION
    # Measures price dispersion from the mean
    # 
    # Formula: sqrt(VAR)
    # 
    # Interpretation:
    #   High STDDEV: High volatility, prices spread out
    #   Low STDDEV: Low volatility, prices clustered
    #   Rising STDDEV: Volatility increasing
    #   Falling STDDEV: Volatility decreasing
    # 
    # Use Cases:
    #   - Bollinger Bands use STDDEV for band width
    #   - Volatility measurement
    #   - Position sizing (smaller positions when high)
    #   - Breakout detection (low STDDEV → breakout coming)
    # =========================================================================
    try:
        stddev = talib.STDDEV(close, timeperiod=5, nbdev=1)
        result.stddev_5 = _safe_last(stddev)
        result.stddev_array = stddev
    except Exception as e:
        print(f"STDDEV error: {e}")
    
    # =========================================================================
    # VAR - VARIANCE
    # Square of standard deviation
    # 
    # Formula: SUM((Close - SMA)^2) / n
    # 
    # Interpretation:
    #   Same as STDDEV but squared
    #   Used in statistical calculations
    #   Less intuitive than STDDEV for trading
    # =========================================================================
    try:
        var = talib.VAR(close, timeperiod=5, nbdev=1)
        result.var_5 = _safe_last(var)
    except Exception as e:
        print(f"VAR error: {e}")
    
    # =========================================================================
    # TSF - TIME SERIES FORECAST
    # Projects the linear regression line one bar forward
    # 
    # Formula: LINEARREG + LINEARREG_SLOPE
    # 
    # Interpretation:
    #   Predicts where price "should" be based on trend
    #   Price > TSF: Price ahead of trend (bullish momentum)
    #   Price < TSF: Price behind trend (bearish momentum)
    # 
    # Use Cases:
    #   - Short-term price projection
    #   - Trend-following signals
    #   - Identifying momentum shifts
    # =========================================================================
    try:
        tsf = talib.TSF(close, timeperiod=14)
        result.tsf_14 = _safe_last(tsf)
    except Exception as e:
        print(f"TSF error: {e}")
    
    # =========================================================================
    # BETA - BETA COEFFICIENT
    # Measures relationship between two price series
    # Here we use High vs Low to measure range expansion
    # 
    # Formula: Covariance(X,Y) / Variance(X)
    # 
    # Interpretation (High vs Low):
    #   Beta > 1: Range expanding
    #   Beta < 1: Range contracting
    #   Beta = 1: Stable range
    # 
    # Traditional use (stock vs market):
    #   Beta > 1: More volatile than market
    #   Beta < 1: Less volatile than market
    # =========================================================================
    try:
        beta = talib.BETA(high, low, timeperiod=5)
        result.beta_5 = _safe_last(beta)
    except Exception as e:
        print(f"BETA error: {e}")
    
    # =========================================================================
    # CORREL - PEARSON CORRELATION COEFFICIENT
    # Measures linear correlation between two series
    # Here we use High vs Low
    # 
    # Formula: Covariance(X,Y) / (STDDEV(X) * STDDEV(Y))
    # Range: -1 to +1
    # 
    # Interpretation (High vs Low):
    #   Always positive (highs and lows move together)
    #   Near 1: Strong positive correlation (normal)
    #   Lower values: Unusual divergence
    # 
    # Traditional use (comparing assets):
    #   +1: Perfect positive correlation
    #   0: No correlation
    #   -1: Perfect negative correlation
    # =========================================================================
    try:
        correl = talib.CORREL(high, low, timeperiod=30)
        result.correl_30 = _safe_last(correl)
    except Exception as e:
        print(f"CORREL error: {e}")
    
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


def get_statistics_dict(result: StatisticsResult) -> Dict[str, Any]:
    """Convert StatisticsResult to dictionary for JSON output."""
    return {
        "LINEARREG_14": result.linearreg_14,
        "LINEARREG_ANGLE_14": result.linearreg_angle_14,
        "LINEARREG_INTERCEPT_14": result.linearreg_intercept_14,
        "LINEARREG_SLOPE_14": result.linearreg_slope_14,
        "STDDEV_5": result.stddev_5,
        "VAR_5": result.var_5,
        "TSF_14": result.tsf_14,
        "BETA_5": result.beta_5,
        "CORREL_30": result.correl_30,
    }


def interpret_statistics(result: StatisticsResult, current_price: float) -> Dict[str, str]:
    """
    Interpret statistical indicators.
    
    Args:
        result: StatisticsResult with computed values
        current_price: Current close price
    
    Returns:
        Dict with interpretations
    """
    interpretations = {}
    
    # Linear Regression Angle - Trend strength
    if result.linearreg_angle_14 is not None:
        angle = result.linearreg_angle_14
        if angle > 45:
            interpretations["LINEARREG_ANGLE"] = f"STRONG UPTREND ({angle:.1f}°)"
        elif angle > 20:
            interpretations["LINEARREG_ANGLE"] = f"Moderate uptrend ({angle:.1f}°)"
        elif angle > -20:
            interpretations["LINEARREG_ANGLE"] = f"SIDEWAYS ({angle:.1f}°)"
        elif angle > -45:
            interpretations["LINEARREG_ANGLE"] = f"Moderate downtrend ({angle:.1f}°)"
        else:
            interpretations["LINEARREG_ANGLE"] = f"STRONG DOWNTREND ({angle:.1f}°)"
    
    # Linear Regression Slope - Trend direction
    if result.linearreg_slope_14 is not None:
        slope = result.linearreg_slope_14
        if slope > 0:
            interpretations["LINEARREG_SLOPE"] = f"Positive slope ({slope:.5f}) - Upward trend"
        else:
            interpretations["LINEARREG_SLOPE"] = f"Negative slope ({slope:.5f}) - Downward trend"
    
    # Price vs Linear Regression
    if result.linearreg_14 is not None:
        if current_price > result.linearreg_14:
            diff_pct = ((current_price - result.linearreg_14) / result.linearreg_14) * 100
            interpretations["LINEARREG"] = f"Price ABOVE regression by {diff_pct:.2f}%"
        else:
            diff_pct = ((result.linearreg_14 - current_price) / result.linearreg_14) * 100
            interpretations["LINEARREG"] = f"Price BELOW regression by {diff_pct:.2f}%"
    
    # TSF - Forecast
    if result.tsf_14 is not None:
        if current_price > result.tsf_14:
            interpretations["TSF"] = "Price ahead of forecast - Bullish momentum"
        else:
            interpretations["TSF"] = "Price behind forecast - Bearish momentum"
    
    # Standard Deviation - Volatility
    if result.stddev_array is not None and len(result.stddev_array) > 20:
        recent_stddev = np.nanmean(result.stddev_array[-5:])
        older_stddev = np.nanmean(result.stddev_array[-20:-5])
        
        if recent_stddev > older_stddev * 1.5:
            interpretations["STDDEV"] = "Volatility EXPANDING - Potential breakout or reversal"
        elif recent_stddev < older_stddev * 0.5:
            interpretations["STDDEV"] = "Volatility CONTRACTING - Consolidation, breakout may follow"
        else:
            interpretations["STDDEV"] = "Volatility STABLE"
    
    return interpretations


def calculate_regression_channel(
    close: np.ndarray,
    period: int = 14,
    num_stddev: float = 2.0
) -> Dict[str, float]:
    """
    Calculate linear regression channel (like Bollinger but with regression).
    
    Args:
        close: Close prices
        period: Regression period
        num_stddev: Number of standard deviations for channel
    
    Returns:
        Dict with upper, middle (regression), and lower channel values
    """
    if len(close) < period:
        return {"upper": None, "middle": None, "lower": None}
    
    linearreg = talib.LINEARREG(close, timeperiod=period)
    stddev = talib.STDDEV(close, timeperiod=period, nbdev=1)
    
    middle = _safe_last(linearreg)
    std = _safe_last(stddev)
    
    if middle is None or std is None:
        return {"upper": None, "middle": None, "lower": None}
    
    return {
        "upper": round(middle + (std * num_stddev), 5),
        "middle": round(middle, 5),
        "lower": round(middle - (std * num_stddev), 5),
        "channel_width": round(std * num_stddev * 2, 5)
    }
