"""
Kuiper V2 - Math Transform Functions (15 Functions)
====================================================

All 15 TA-Lib Math Transform functions.
These apply mathematical transformations to price data.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
ALL CLOSE ONLY:
- ACOS(close)   # Arc Cosine
- ASIN(close)   # Arc Sine
- ATAN(close)   # Arc Tangent
- CEIL(close)   # Ceiling
- COS(close)    # Cosine
- COSH(close)   # Hyperbolic Cosine
- EXP(close)    # Exponential
- FLOOR(close)  # Floor
- LN(close)     # Natural Logarithm
- LOG10(close)  # Base-10 Logarithm
- SIN(close)    # Sine
- SINH(close)   # Hyperbolic Sine
- SQRT(close)   # Square Root
- TAN(close)    # Tangent
- TANH(close)   # Hyperbolic Tangent

NOTE: Most of these are rarely used directly in trading.
The most useful are: LN, LOG10, SQRT for normalization.
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MathTransformResult:
    """Container for math transform results."""
    
    # Most useful transforms
    ln: Optional[float] = None       # Natural log - useful for returns
    log10: Optional[float] = None    # Log base 10
    sqrt: Optional[float] = None     # Square root
    ceil: Optional[float] = None     # Ceiling
    floor: Optional[float] = None    # Floor
    exp: Optional[float] = None      # Exponential
    
    # Trigonometric (rarely used in trading)
    acos: Optional[float] = None
    asin: Optional[float] = None
    atan: Optional[float] = None
    cos: Optional[float] = None
    cosh: Optional[float] = None
    sin: Optional[float] = None
    sinh: Optional[float] = None
    tan: Optional[float] = None
    tanh: Optional[float] = None


def compute_math_transform(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> MathTransformResult:
    """
    Compute all 15 Math Transform functions.
    
    Note: Most of these are mathematical utilities rather than
    trading indicators. The most useful are:
    - LN: For calculating log returns
    - SQRT: For volatility calculations
    - CEIL/FLOOR: For rounding price levels
    
    Args:
        open_: Open prices (not used)
        high: High prices (not used)
        low: Low prices (not used)
        close: Close prices (numpy array)
        volume: Volume (not used)
    
    Returns:
        MathTransformResult with all values
    """
    result = MathTransformResult()
    
    if len(close) < 1:
        return result
    
    # =========================================================================
    # LN - NATURAL LOGARITHM
    # Most useful for calculating log returns
    # Log Return = ln(Price_t / Price_t-1) = ln(Price_t) - ln(Price_t-1)
    # =========================================================================
    try:
        ln = talib.LN(close)
        result.ln = _safe_last(ln)
    except Exception as e:
        pass
    
    # =========================================================================
    # LOG10 - BASE-10 LOGARITHM
    # Useful for scaling large price differences
    # =========================================================================
    try:
        log10 = talib.LOG10(close)
        result.log10 = _safe_last(log10)
    except Exception as e:
        pass
    
    # =========================================================================
    # SQRT - SQUARE ROOT
    # Used in volatility calculations (variance -> stddev)
    # =========================================================================
    try:
        sqrt = talib.SQRT(close)
        result.sqrt = _safe_last(sqrt)
    except Exception as e:
        pass
    
    # =========================================================================
    # CEIL - CEILING
    # Rounds up to nearest integer
    # Useful for price level calculations
    # =========================================================================
    try:
        ceil = talib.CEIL(close)
        result.ceil = _safe_last(ceil)
    except Exception as e:
        pass
    
    # =========================================================================
    # FLOOR - FLOOR
    # Rounds down to nearest integer
    # Useful for price level calculations
    # =========================================================================
    try:
        floor = talib.FLOOR(close)
        result.floor = _safe_last(floor)
    except Exception as e:
        pass
    
    # =========================================================================
    # EXP - EXPONENTIAL
    # e^x - inverse of natural log
    # =========================================================================
    try:
        exp = talib.EXP(close)
        result.exp = _safe_last(exp)
    except Exception as e:
        pass
    
    # =========================================================================
    # TRIGONOMETRIC FUNCTIONS
    # Rarely used directly in trading, but included for completeness
    # =========================================================================
    try:
        result.acos = _safe_last(talib.ACOS(close))
    except:
        pass
    
    try:
        result.asin = _safe_last(talib.ASIN(close))
    except:
        pass
    
    try:
        result.atan = _safe_last(talib.ATAN(close))
    except:
        pass
    
    try:
        result.cos = _safe_last(talib.COS(close))
    except:
        pass
    
    try:
        result.cosh = _safe_last(talib.COSH(close))
    except:
        pass
    
    try:
        result.sin = _safe_last(talib.SIN(close))
    except:
        pass
    
    try:
        result.sinh = _safe_last(talib.SINH(close))
    except:
        pass
    
    try:
        result.tan = _safe_last(talib.TAN(close))
    except:
        pass
    
    try:
        result.tanh = _safe_last(talib.TANH(close))
    except:
        pass
    
    return result


def _safe_last(arr: np.ndarray) -> Optional[float]:
    """Safely get the last non-NaN value from array."""
    if arr is None or len(arr) == 0:
        return None
    
    val = arr[-1]
    
    if np.isnan(val) or np.isinf(val):
        valid = arr[~(np.isnan(arr) | np.isinf(arr))]
        if len(valid) > 0:
            return float(valid[-1])
        return None
    
    return float(val)


def get_math_transform_dict(result: MathTransformResult) -> Dict[str, Any]:
    """Convert MathTransformResult to dictionary for JSON output."""
    return {
        "LN": result.ln,
        "LOG10": result.log10,
        "SQRT": result.sqrt,
        "CEIL": result.ceil,
        "FLOOR": result.floor,
        "EXP": result.exp,
        # Trig functions (rarely used)
        "ACOS": result.acos,
        "ASIN": result.asin,
        "ATAN": result.atan,
        "COS": result.cos,
        "COSH": result.cosh,
        "SIN": result.sin,
        "SINH": result.sinh,
        "TAN": result.tan,
        "TANH": result.tanh,
    }


def calculate_log_returns(close: np.ndarray) -> np.ndarray:
    """
    Calculate log returns from close prices.
    
    Log returns are preferred for:
    - Time-additivity (can sum across periods)
    - Approximate normality
    - Symmetric treatment of gains/losses
    
    Args:
        close: Close prices
    
    Returns:
        Array of log returns
    """
    if len(close) < 2:
        return np.array([])
    
    ln_prices = talib.LN(close)
    returns = np.diff(ln_prices)
    
    return returns
