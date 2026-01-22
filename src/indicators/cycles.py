"""
Kuiper V2 - Cycle Indicators (5 Functions)
==========================================

All 5 TA-Lib Hilbert Transform Cycle functions.
These are John Ehlers' cycle analysis indicators.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
ALL CLOSE ONLY, ALL HAVE UNSTABLE PERIOD:
- HT_DCPERIOD(close)     # Dominant Cycle Period
- HT_DCPHASE(close)      # Dominant Cycle Phase
- HT_PHASOR(close)       # returns (inphase, quadrature)
- HT_SINE(close)         # returns (sine, leadsine)
- HT_TRENDMODE(close)    # returns integer (0=cycle, 1=trend)
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CycleResult:
    """Container for all cycle indicator results."""
    
    # Dominant Cycle Period (in bars)
    ht_dcperiod: Optional[float] = None
    
    # Dominant Cycle Phase (in degrees, 0-360)
    ht_dcphase: Optional[float] = None
    
    # Phasor Components
    ht_phasor_inphase: Optional[float] = None
    ht_phasor_quadrature: Optional[float] = None
    
    # Sine Wave
    ht_sine: Optional[float] = None
    ht_leadsine: Optional[float] = None
    
    # Trend vs Cycle Mode (0 or 1)
    ht_trendmode: Optional[int] = None
    
    # Full arrays for analysis
    ht_trendmode_array: Optional[np.ndarray] = None
    ht_sine_array: Optional[np.ndarray] = None


def compute_cycles(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> CycleResult:
    """
    Compute all 5 Hilbert Transform Cycle indicators.
    
    These indicators use the Hilbert Transform to analyze market cycles.
    They help identify:
    - Whether market is trending or cycling
    - The dominant cycle period
    - The current phase within the cycle
    
    Args:
        open_: Open prices (numpy array) - not used
        high: High prices (numpy array) - not used
        low: Low prices (numpy array) - not used
        close: Close prices (numpy array)
        volume: Volume (numpy array) - not used
    
    Returns:
        CycleResult with all indicator values
    """
    result = CycleResult()
    
    if len(close) < 64:  # Hilbert Transform needs significant data
        return result
    
    # =========================================================================
    # HT_DCPERIOD - HILBERT TRANSFORM DOMINANT CYCLE PERIOD
    # Measures the dominant cycle period in the data
    # Output: Number of bars in the dominant cycle
    # 
    # Interpretation:
    #   Typical range: 10-50 bars
    #   Shorter period: Faster cycles, more volatile
    #   Longer period: Slower cycles, more stable
    #   Period changes: Market character changing
    # 
    # Use Cases:
    #   - Adaptive indicator periods (use DC period instead of fixed)
    #   - Identifying cycle length for mean reversion
    #   - Detecting when market rhythm changes
    # 
    # NOTE: Has unstable period (~63 bars)
    # =========================================================================
    try:
        dcperiod = talib.HT_DCPERIOD(close)
        result.ht_dcperiod = _safe_last(dcperiod)
    except Exception as e:
        print(f"HT_DCPERIOD error: {e}")
    
    # =========================================================================
    # HT_DCPHASE - HILBERT TRANSFORM DOMINANT CYCLE PHASE
    # Measures the phase angle of the dominant cycle
    # Output: Phase in degrees (0-360)
    # 
    # Interpretation:
    #   0° / 360°: Cycle bottom
    #   90°: Rising phase (bullish)
    #   180°: Cycle top
    #   270°: Falling phase (bearish)
    # 
    # Use Cases:
    #   - Timing entries at cycle bottoms (near 0°/360°)
    #   - Timing exits at cycle tops (near 180°)
    #   - Confirming trend direction with phase direction
    # 
    # NOTE: Has unstable period
    # =========================================================================
    try:
        dcphase = talib.HT_DCPHASE(close)
        result.ht_dcphase = _safe_last(dcphase)
    except Exception as e:
        print(f"HT_DCPHASE error: {e}")
    
    # =========================================================================
    # HT_PHASOR - HILBERT TRANSFORM PHASOR COMPONENTS
    # Returns the in-phase and quadrature components
    # Output: (inphase, quadrature) - two arrays
    # 
    # The phasor represents the cycle as a rotating vector:
    #   - InPhase: Real component (cosine)
    #   - Quadrature: Imaginary component (sine)
    # 
    # Interpretation:
    #   InPhase > 0, Quadrature > 0: Rising phase
    #   InPhase < 0, Quadrature > 0: Topping phase
    #   InPhase < 0, Quadrature < 0: Falling phase
    #   InPhase > 0, Quadrature < 0: Bottoming phase
    # 
    # Use Cases:
    #   - Advanced cycle analysis
    #   - Determining cycle phase more precisely
    #   - Building adaptive indicators
    # 
    # NOTE: Has unstable period
    # =========================================================================
    try:
        inphase, quadrature = talib.HT_PHASOR(close)
        result.ht_phasor_inphase = _safe_last(inphase)
        result.ht_phasor_quadrature = _safe_last(quadrature)
    except Exception as e:
        print(f"HT_PHASOR error: {e}")
    
    # =========================================================================
    # HT_SINE - HILBERT TRANSFORM SINEWAVE
    # Generates sine wave representation of the dominant cycle
    # Output: (sine, leadsine) - sine and leading sine
    # 
    # The LeadSine leads the Sine by 45 degrees (1/8 cycle)
    # 
    # Interpretation:
    #   Sine crossing above LeadSine: Cycle turning up (buy signal in ranging)
    #   Sine crossing below LeadSine: Cycle turning down (sell signal in ranging)
    #   Both near extremes (+1 or -1): Cycle at top or bottom
    # 
    # IMPORTANT: Only use in RANGING markets (HT_TRENDMODE = 0)
    # In trending markets, these signals are unreliable
    # 
    # NOTE: Has unstable period
    # =========================================================================
    try:
        sine, leadsine = talib.HT_SINE(close)
        result.ht_sine = _safe_last(sine)
        result.ht_leadsine = _safe_last(leadsine)
        result.ht_sine_array = sine
    except Exception as e:
        print(f"HT_SINE error: {e}")
    
    # =========================================================================
    # HT_TRENDMODE - HILBERT TRANSFORM TREND VS CYCLE MODE
    # Determines if market is trending or cycling
    # Output: Integer (0 = Cycle Mode, 1 = Trend Mode)
    # 
    # This is CRITICAL for the Wisdom Engine:
    #   - Mode 0 (Cycle): Use oscillators, mean reversion strategies
    #   - Mode 1 (Trend): Use trend-following strategies
    # 
    # Interpretation:
    #   0: Market is in cycle/ranging mode
    #      - RSI overbought/oversold signals are valid
    #      - Mean reversion strategies work
    #      - HT_SINE crossovers are valid signals
    #   
    #   1: Market is in trend mode
    #      - Ignore overbought/oversold (can stay extreme)
    #      - Use trend-following strategies
    #      - HT_SINE signals are unreliable
    # 
    # NOTE: Has unstable period
    # =========================================================================
    try:
        trendmode = talib.HT_TRENDMODE(close)
        result.ht_trendmode = int(_safe_last(trendmode)) if _safe_last(trendmode) is not None else None
        result.ht_trendmode_array = trendmode
    except Exception as e:
        print(f"HT_TRENDMODE error: {e}")
    
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


def get_cycles_dict(result: CycleResult) -> Dict[str, Any]:
    """Convert CycleResult to dictionary for JSON output."""
    return {
        "HT_DCPERIOD": result.ht_dcperiod,
        "HT_DCPHASE": result.ht_dcphase,
        "HT_PHASOR_inphase": result.ht_phasor_inphase,
        "HT_PHASOR_quadrature": result.ht_phasor_quadrature,
        "HT_SINE_sine": result.ht_sine,
        "HT_SINE_leadsine": result.ht_leadsine,
        "HT_TRENDMODE": result.ht_trendmode,
    }


def interpret_cycles(result: CycleResult) -> Dict[str, str]:
    """
    Interpret cycle indicators.
    
    Args:
        result: CycleResult with computed values
    
    Returns:
        Dict with interpretations
    """
    interpretations = {}
    
    # Trend Mode - Most important
    if result.ht_trendmode is not None:
        if result.ht_trendmode == 1:
            interpretations["HT_TRENDMODE"] = "TREND MODE - Use trend-following strategies, ignore overbought/oversold"
        else:
            interpretations["HT_TRENDMODE"] = "CYCLE MODE - Mean reversion valid, oscillator signals reliable"
    
    # Dominant Cycle Period
    if result.ht_dcperiod is not None:
        period = result.ht_dcperiod
        if period < 15:
            interpretations["HT_DCPERIOD"] = f"SHORT cycle ({period:.0f} bars) - Fast market rhythm"
        elif period > 40:
            interpretations["HT_DCPERIOD"] = f"LONG cycle ({period:.0f} bars) - Slow market rhythm"
        else:
            interpretations["HT_DCPERIOD"] = f"NORMAL cycle ({period:.0f} bars)"
    
    # Cycle Phase
    if result.ht_dcphase is not None:
        phase = result.ht_dcphase
        if 0 <= phase < 45 or phase >= 315:
            interpretations["HT_DCPHASE"] = f"CYCLE BOTTOM ({phase:.0f}°) - Potential buy zone in ranging market"
        elif 45 <= phase < 135:
            interpretations["HT_DCPHASE"] = f"RISING PHASE ({phase:.0f}°) - Bullish cycle momentum"
        elif 135 <= phase < 225:
            interpretations["HT_DCPHASE"] = f"CYCLE TOP ({phase:.0f}°) - Potential sell zone in ranging market"
        else:
            interpretations["HT_DCPHASE"] = f"FALLING PHASE ({phase:.0f}°) - Bearish cycle momentum"
    
    # Sine Wave (only meaningful in cycle mode)
    if result.ht_trendmode == 0 and result.ht_sine is not None and result.ht_leadsine is not None:
        if result.ht_sine > result.ht_leadsine:
            interpretations["HT_SINE"] = "Sine > LeadSine - Cycle turning UP (bullish in ranging)"
        else:
            interpretations["HT_SINE"] = "Sine < LeadSine - Cycle turning DOWN (bearish in ranging)"
    elif result.ht_trendmode == 1:
        interpretations["HT_SINE"] = "In trend mode - Sine wave signals not reliable"
    
    return interpretations


def get_adaptive_period(result: CycleResult, default: int = 14) -> int:
    """
    Get adaptive indicator period based on dominant cycle.
    
    Instead of using fixed periods (like RSI 14), use the dominant
    cycle period for more responsive indicators.
    
    Args:
        result: CycleResult with HT_DCPERIOD
        default: Default period if cycle period unavailable
    
    Returns:
        Adaptive period (clamped to reasonable range)
    """
    if result.ht_dcperiod is None:
        return default
    
    # Clamp to reasonable range
    period = int(result.ht_dcperiod)
    return max(5, min(50, period))
