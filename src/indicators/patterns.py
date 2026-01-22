"""
Kuiper V2 - Pattern Recognition (61 Functions)
===============================================

All 61 TA-Lib Candlestick Pattern Recognition functions.
ALL patterns require: open, high, low, close

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
ALL PATTERNS: CDL*(open, high, low, close)
Some have optional penetration parameter:
- CDLABANDONEDBABY(open, high, low, close, penetration=0)
- CDLDARKCLOUDCOVER(open, high, low, close, penetration=0)
- CDLEVENINGDOJISTAR(open, high, low, close, penetration=0)
- CDLEVENINGSTAR(open, high, low, close, penetration=0)
- CDLMATHOLD(open, high, low, close, penetration=0)
- CDLMORNINGDOJISTAR(open, high, low, close, penetration=0)
- CDLMORNINGSTAR(open, high, low, close, penetration=0)

OUTPUT: Integer values
- 100: Bullish pattern detected
- 0: No pattern
- -100: Bearish pattern detected
"""

import numpy as np
import talib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class PatternResult:
    """Container for all candlestick pattern results."""
    
    # All 61 patterns stored in a dict
    patterns: Dict[str, int] = field(default_factory=dict)
    
    # Categorized patterns
    bullish_patterns: List[str] = field(default_factory=list)
    bearish_patterns: List[str] = field(default_factory=list)
    
    # Pattern counts
    bullish_count: int = 0
    bearish_count: int = 0


# Pattern categories for interpretation
REVERSAL_PATTERNS = {
    "bullish_reversal": [
        "CDL3WHITESOLDIERS", "CDLABANDONEDBABY", "CDLENGULFING",
        "CDLHAMMER", "CDLINVERTEDHAMMER", "CDLMORNINGDOJISTAR",
        "CDLMORNINGSTAR", "CDLPIERCING", "CDL3INSIDE",
        "CDLHARAMI", "CDLHARAMICROSS", "CDLKICKING",
        "CDLKICKINGBYLENGTH", "CDLTAKURI", "CDLDRAGONFLYDOJI"
    ],
    "bearish_reversal": [
        "CDL3BLACKCROWS", "CDLABANDONEDBABY", "CDLENGULFING",
        "CDLHANGINGMAN", "CDLSHOOTINGSTAR", "CDLEVENINGDOJISTAR",
        "CDLEVENINGSTAR", "CDLDARKCLOUDCOVER", "CDL3INSIDE",
        "CDLHARAMI", "CDLHARAMICROSS", "CDLKICKING",
        "CDLKICKINGBYLENGTH", "CDLGRAVESTONEDOJI"
    ],
    "continuation": [
        "CDL3LINESTRIKE", "CDLGAPSIDESIDEWHITE", "CDLMATHOLD",
        "CDLRISEFALL3METHODS", "CDLSEPARATINGLINES", "CDLTASUKIGAP",
        "CDLTHRUSTING", "CDLONNECK", "CDLINNECK"
    ],
    "indecision": [
        "CDLDOJI", "CDLDOJISTAR", "CDLLONGLEGGEDDOJI",
        "CDLSPINNINGTOP", "CDLHIGHWAVE", "CDLRICKSHAWMAN"
    ]
}


def compute_patterns(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> PatternResult:
    """
    Compute all 61 Candlestick Pattern Recognition functions.
    
    Args:
        open_: Open prices (numpy array)
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array) - not used for patterns
    
    Returns:
        PatternResult with all pattern values and categorization
    """
    result = PatternResult()
    
    if len(close) < 10:
        return result
    
    # =========================================================================
    # TWO CROWS
    # Bearish reversal pattern
    # =========================================================================
    try:
        val = talib.CDL2CROWS(open_, high, low, close)
        result.patterns["CDL2CROWS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL2CROWS"] = 0
    
    # =========================================================================
    # THREE BLACK CROWS
    # Strong bearish reversal - three consecutive long black candles
    # =========================================================================
    try:
        val = talib.CDL3BLACKCROWS(open_, high, low, close)
        result.patterns["CDL3BLACKCROWS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL3BLACKCROWS"] = 0
    
    # =========================================================================
    # THREE INSIDE UP/DOWN
    # Reversal pattern - harami followed by confirmation
    # =========================================================================
    try:
        val = talib.CDL3INSIDE(open_, high, low, close)
        result.patterns["CDL3INSIDE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL3INSIDE"] = 0
    
    # =========================================================================
    # THREE LINE STRIKE
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDL3LINESTRIKE(open_, high, low, close)
        result.patterns["CDL3LINESTRIKE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL3LINESTRIKE"] = 0
    
    # =========================================================================
    # THREE OUTSIDE UP/DOWN
    # Reversal pattern - engulfing followed by confirmation
    # =========================================================================
    try:
        val = talib.CDL3OUTSIDE(open_, high, low, close)
        result.patterns["CDL3OUTSIDE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL3OUTSIDE"] = 0
    
    # =========================================================================
    # THREE STARS IN THE SOUTH
    # Bullish reversal pattern
    # =========================================================================
    try:
        val = talib.CDL3STARSINSOUTH(open_, high, low, close)
        result.patterns["CDL3STARSINSOUTH"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL3STARSINSOUTH"] = 0
    
    # =========================================================================
    # THREE WHITE SOLDIERS
    # Strong bullish reversal - three consecutive long white candles
    # =========================================================================
    try:
        val = talib.CDL3WHITESOLDIERS(open_, high, low, close)
        result.patterns["CDL3WHITESOLDIERS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDL3WHITESOLDIERS"] = 0
    
    # =========================================================================
    # ABANDONED BABY
    # Strong reversal pattern with gap
    # =========================================================================
    try:
        val = talib.CDLABANDONEDBABY(open_, high, low, close, penetration=0)
        result.patterns["CDLABANDONEDBABY"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLABANDONEDBABY"] = 0
    
    # =========================================================================
    # ADVANCE BLOCK
    # Bearish reversal - weakening uptrend
    # =========================================================================
    try:
        val = talib.CDLADVANCEBLOCK(open_, high, low, close)
        result.patterns["CDLADVANCEBLOCK"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLADVANCEBLOCK"] = 0
    
    # =========================================================================
    # BELT HOLD
    # Reversal pattern
    # =========================================================================
    try:
        val = talib.CDLBELTHOLD(open_, high, low, close)
        result.patterns["CDLBELTHOLD"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLBELTHOLD"] = 0
    
    # =========================================================================
    # BREAKAWAY
    # Reversal pattern
    # =========================================================================
    try:
        val = talib.CDLBREAKAWAY(open_, high, low, close)
        result.patterns["CDLBREAKAWAY"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLBREAKAWAY"] = 0
    
    # =========================================================================
    # CLOSING MARUBOZU
    # Strong momentum candle
    # =========================================================================
    try:
        val = talib.CDLCLOSINGMARUBOZU(open_, high, low, close)
        result.patterns["CDLCLOSINGMARUBOZU"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLCLOSINGMARUBOZU"] = 0
    
    # =========================================================================
    # CONCEALING BABY SWALLOW
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLCONCEALBABYSWALL(open_, high, low, close)
        result.patterns["CDLCONCEALBABYSWALL"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLCONCEALBABYSWALL"] = 0
    
    # =========================================================================
    # COUNTERATTACK
    # Reversal pattern
    # =========================================================================
    try:
        val = talib.CDLCOUNTERATTACK(open_, high, low, close)
        result.patterns["CDLCOUNTERATTACK"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLCOUNTERATTACK"] = 0
    
    # =========================================================================
    # DARK CLOUD COVER
    # Bearish reversal
    # =========================================================================
    try:
        val = talib.CDLDARKCLOUDCOVER(open_, high, low, close, penetration=0)
        result.patterns["CDLDARKCLOUDCOVER"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLDARKCLOUDCOVER"] = 0

    # =========================================================================
    # DOJI
    # Indecision pattern - open equals close
    # =========================================================================
    try:
        val = talib.CDLDOJI(open_, high, low, close)
        result.patterns["CDLDOJI"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLDOJI"] = 0
    
    # =========================================================================
    # DOJI STAR
    # Reversal pattern with doji
    # =========================================================================
    try:
        val = talib.CDLDOJISTAR(open_, high, low, close)
        result.patterns["CDLDOJISTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLDOJISTAR"] = 0
    
    # =========================================================================
    # DRAGONFLY DOJI
    # Bullish reversal doji
    # =========================================================================
    try:
        val = talib.CDLDRAGONFLYDOJI(open_, high, low, close)
        result.patterns["CDLDRAGONFLYDOJI"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLDRAGONFLYDOJI"] = 0
    
    # =========================================================================
    # ENGULFING PATTERN
    # Strong reversal - current candle engulfs previous
    # =========================================================================
    try:
        val = talib.CDLENGULFING(open_, high, low, close)
        result.patterns["CDLENGULFING"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLENGULFING"] = 0
    
    # =========================================================================
    # EVENING DOJI STAR
    # Bearish reversal with doji
    # =========================================================================
    try:
        val = talib.CDLEVENINGDOJISTAR(open_, high, low, close, penetration=0)
        result.patterns["CDLEVENINGDOJISTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLEVENINGDOJISTAR"] = 0
    
    # =========================================================================
    # EVENING STAR
    # Bearish reversal
    # =========================================================================
    try:
        val = talib.CDLEVENINGSTAR(open_, high, low, close, penetration=0)
        result.patterns["CDLEVENINGSTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLEVENINGSTAR"] = 0
    
    # =========================================================================
    # GAP SIDE-BY-SIDE WHITE LINES
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLGAPSIDESIDEWHITE(open_, high, low, close)
        result.patterns["CDLGAPSIDESIDEWHITE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLGAPSIDESIDEWHITE"] = 0
    
    # =========================================================================
    # GRAVESTONE DOJI
    # Bearish reversal doji
    # =========================================================================
    try:
        val = talib.CDLGRAVESTONEDOJI(open_, high, low, close)
        result.patterns["CDLGRAVESTONEDOJI"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLGRAVESTONEDOJI"] = 0
    
    # =========================================================================
    # HAMMER
    # Bullish reversal at bottom
    # =========================================================================
    try:
        val = talib.CDLHAMMER(open_, high, low, close)
        result.patterns["CDLHAMMER"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHAMMER"] = 0
    
    # =========================================================================
    # HANGING MAN
    # Bearish reversal at top
    # =========================================================================
    try:
        val = talib.CDLHANGINGMAN(open_, high, low, close)
        result.patterns["CDLHANGINGMAN"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHANGINGMAN"] = 0
    
    # =========================================================================
    # HARAMI
    # Reversal pattern - inside bar
    # =========================================================================
    try:
        val = talib.CDLHARAMI(open_, high, low, close)
        result.patterns["CDLHARAMI"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHARAMI"] = 0
    
    # =========================================================================
    # HARAMI CROSS
    # Reversal pattern with doji inside
    # =========================================================================
    try:
        val = talib.CDLHARAMICROSS(open_, high, low, close)
        result.patterns["CDLHARAMICROSS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHARAMICROSS"] = 0
    
    # =========================================================================
    # HIGH WAVE
    # Indecision pattern
    # =========================================================================
    try:
        val = talib.CDLHIGHWAVE(open_, high, low, close)
        result.patterns["CDLHIGHWAVE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHIGHWAVE"] = 0
    
    # =========================================================================
    # HIKKAKE
    # Reversal pattern
    # =========================================================================
    try:
        val = talib.CDLHIKKAKE(open_, high, low, close)
        result.patterns["CDLHIKKAKE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHIKKAKE"] = 0
    
    # =========================================================================
    # MODIFIED HIKKAKE
    # Modified reversal pattern
    # =========================================================================
    try:
        val = talib.CDLHIKKAKEMOD(open_, high, low, close)
        result.patterns["CDLHIKKAKEMOD"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHIKKAKEMOD"] = 0
    
    # =========================================================================
    # HOMING PIGEON
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLHOMINGPIGEON(open_, high, low, close)
        result.patterns["CDLHOMINGPIGEON"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLHOMINGPIGEON"] = 0
    
    # =========================================================================
    # IDENTICAL THREE CROWS
    # Bearish reversal
    # =========================================================================
    try:
        val = talib.CDLIDENTICAL3CROWS(open_, high, low, close)
        result.patterns["CDLIDENTICAL3CROWS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLIDENTICAL3CROWS"] = 0
    
    # =========================================================================
    # IN-NECK
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLINNECK(open_, high, low, close)
        result.patterns["CDLINNECK"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLINNECK"] = 0
    
    # =========================================================================
    # INVERTED HAMMER
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLINVERTEDHAMMER(open_, high, low, close)
        result.patterns["CDLINVERTEDHAMMER"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLINVERTEDHAMMER"] = 0
    
    # =========================================================================
    # KICKING
    # Strong reversal pattern
    # =========================================================================
    try:
        val = talib.CDLKICKING(open_, high, low, close)
        result.patterns["CDLKICKING"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLKICKING"] = 0
    
    # =========================================================================
    # KICKING BY LENGTH
    # Strong reversal pattern
    # =========================================================================
    try:
        val = talib.CDLKICKINGBYLENGTH(open_, high, low, close)
        result.patterns["CDLKICKINGBYLENGTH"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLKICKINGBYLENGTH"] = 0
    
    # =========================================================================
    # LADDER BOTTOM
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLLADDERBOTTOM(open_, high, low, close)
        result.patterns["CDLLADDERBOTTOM"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLLADDERBOTTOM"] = 0
    
    # =========================================================================
    # LONG LEGGED DOJI
    # Indecision pattern
    # =========================================================================
    try:
        val = talib.CDLLONGLEGGEDDOJI(open_, high, low, close)
        result.patterns["CDLLONGLEGGEDDOJI"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLLONGLEGGEDDOJI"] = 0
    
    # =========================================================================
    # LONG LINE CANDLE
    # Strong momentum
    # =========================================================================
    try:
        val = talib.CDLLONGLINE(open_, high, low, close)
        result.patterns["CDLLONGLINE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLLONGLINE"] = 0
    
    # =========================================================================
    # MARUBOZU
    # Strong momentum - no shadows
    # =========================================================================
    try:
        val = talib.CDLMARUBOZU(open_, high, low, close)
        result.patterns["CDLMARUBOZU"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLMARUBOZU"] = 0
    
    # =========================================================================
    # MATCHING LOW
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLMATCHINGLOW(open_, high, low, close)
        result.patterns["CDLMATCHINGLOW"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLMATCHINGLOW"] = 0
    
    # =========================================================================
    # MAT HOLD
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLMATHOLD(open_, high, low, close, penetration=0)
        result.patterns["CDLMATHOLD"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLMATHOLD"] = 0

    # =========================================================================
    # MORNING DOJI STAR
    # Bullish reversal with doji
    # =========================================================================
    try:
        val = talib.CDLMORNINGDOJISTAR(open_, high, low, close, penetration=0)
        result.patterns["CDLMORNINGDOJISTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLMORNINGDOJISTAR"] = 0
    
    # =========================================================================
    # MORNING STAR
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLMORNINGSTAR(open_, high, low, close, penetration=0)
        result.patterns["CDLMORNINGSTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLMORNINGSTAR"] = 0
    
    # =========================================================================
    # ON-NECK
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLONNECK(open_, high, low, close)
        result.patterns["CDLONNECK"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLONNECK"] = 0
    
    # =========================================================================
    # PIERCING
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLPIERCING(open_, high, low, close)
        result.patterns["CDLPIERCING"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLPIERCING"] = 0
    
    # =========================================================================
    # RICKSHAW MAN
    # Indecision pattern
    # =========================================================================
    try:
        val = talib.CDLRICKSHAWMAN(open_, high, low, close)
        result.patterns["CDLRICKSHAWMAN"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLRICKSHAWMAN"] = 0
    
    # =========================================================================
    # RISING/FALLING THREE METHODS
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLRISEFALL3METHODS(open_, high, low, close)
        result.patterns["CDLRISEFALL3METHODS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLRISEFALL3METHODS"] = 0
    
    # =========================================================================
    # SEPARATING LINES
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLSEPARATINGLINES(open_, high, low, close)
        result.patterns["CDLSEPARATINGLINES"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLSEPARATINGLINES"] = 0
    
    # =========================================================================
    # SHOOTING STAR
    # Bearish reversal
    # =========================================================================
    try:
        val = talib.CDLSHOOTINGSTAR(open_, high, low, close)
        result.patterns["CDLSHOOTINGSTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLSHOOTINGSTAR"] = 0
    
    # =========================================================================
    # SHORT LINE CANDLE
    # Small body candle
    # =========================================================================
    try:
        val = talib.CDLSHORTLINE(open_, high, low, close)
        result.patterns["CDLSHORTLINE"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLSHORTLINE"] = 0
    
    # =========================================================================
    # SPINNING TOP
    # Indecision pattern
    # =========================================================================
    try:
        val = talib.CDLSPINNINGTOP(open_, high, low, close)
        result.patterns["CDLSPINNINGTOP"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLSPINNINGTOP"] = 0
    
    # =========================================================================
    # STALLED PATTERN
    # Bearish reversal
    # =========================================================================
    try:
        val = talib.CDLSTALLEDPATTERN(open_, high, low, close)
        result.patterns["CDLSTALLEDPATTERN"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLSTALLEDPATTERN"] = 0
    
    # =========================================================================
    # STICK SANDWICH
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLSTICKSANDWICH(open_, high, low, close)
        result.patterns["CDLSTICKSANDWICH"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLSTICKSANDWICH"] = 0
    
    # =========================================================================
    # TAKURI (DRAGONFLY DOJI WITH VERY LONG LOWER SHADOW)
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLTAKURI(open_, high, low, close)
        result.patterns["CDLTAKURI"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLTAKURI"] = 0
    
    # =========================================================================
    # TASUKI GAP
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLTASUKIGAP(open_, high, low, close)
        result.patterns["CDLTASUKIGAP"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLTASUKIGAP"] = 0
    
    # =========================================================================
    # THRUSTING
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLTHRUSTING(open_, high, low, close)
        result.patterns["CDLTHRUSTING"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLTHRUSTING"] = 0
    
    # =========================================================================
    # TRISTAR
    # Reversal pattern
    # =========================================================================
    try:
        val = talib.CDLTRISTAR(open_, high, low, close)
        result.patterns["CDLTRISTAR"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLTRISTAR"] = 0
    
    # =========================================================================
    # UNIQUE THREE RIVER
    # Bullish reversal
    # =========================================================================
    try:
        val = talib.CDLUNIQUE3RIVER(open_, high, low, close)
        result.patterns["CDLUNIQUE3RIVER"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLUNIQUE3RIVER"] = 0
    
    # =========================================================================
    # UPSIDE GAP TWO CROWS
    # Bearish reversal
    # =========================================================================
    try:
        val = talib.CDLUPSIDEGAP2CROWS(open_, high, low, close)
        result.patterns["CDLUPSIDEGAP2CROWS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLUPSIDEGAP2CROWS"] = 0
    
    # =========================================================================
    # UPSIDE/DOWNSIDE GAP THREE METHODS
    # Continuation pattern
    # =========================================================================
    try:
        val = talib.CDLXSIDEGAP3METHODS(open_, high, low, close)
        result.patterns["CDLXSIDEGAP3METHODS"] = int(_safe_last(val) or 0)
    except Exception as e:
        result.patterns["CDLXSIDEGAP3METHODS"] = 0
    
    # =========================================================================
    # Categorize detected patterns
    # =========================================================================
    for pattern_name, value in result.patterns.items():
        if value > 0:
            result.bullish_patterns.append(pattern_name)
            result.bullish_count += 1
        elif value < 0:
            result.bearish_patterns.append(pattern_name)
            result.bearish_count += 1
    
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


def get_patterns_dict(result: PatternResult) -> Dict[str, Any]:
    """Convert PatternResult to dictionary for JSON output."""
    return {
        "patterns": result.patterns,
        "bullish_patterns": result.bullish_patterns,
        "bearish_patterns": result.bearish_patterns,
        "bullish_count": result.bullish_count,
        "bearish_count": result.bearish_count,
    }


def interpret_patterns(result: PatternResult, market_regime: str) -> Dict[str, str]:
    """
    Interpret detected patterns in context of market regime.
    
    Args:
        result: PatternResult with detected patterns
        market_regime: "TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE"
    
    Returns:
        Dict with pattern interpretations
    """
    interpretations = {}
    
    # Overall pattern sentiment
    if result.bullish_count > result.bearish_count:
        interpretations["overall"] = f"BULLISH bias ({result.bullish_count} bullish vs {result.bearish_count} bearish patterns)"
    elif result.bearish_count > result.bullish_count:
        interpretations["overall"] = f"BEARISH bias ({result.bearish_count} bearish vs {result.bullish_count} bullish patterns)"
    else:
        interpretations["overall"] = "NEUTRAL - No clear pattern bias"
    
    # Interpret specific patterns based on regime
    for pattern in result.bullish_patterns:
        if market_regime == "TRENDING_DOWN":
            if pattern in REVERSAL_PATTERNS["bullish_reversal"]:
                interpretations[pattern] = f"POTENTIAL REVERSAL - {pattern} in downtrend"
            else:
                interpretations[pattern] = f"Counter-trend signal - {pattern} (use caution)"
        elif market_regime == "TRENDING_UP":
            interpretations[pattern] = f"Trend continuation - {pattern} confirms uptrend"
        else:
            interpretations[pattern] = f"Bullish signal - {pattern}"
    
    for pattern in result.bearish_patterns:
        if market_regime == "TRENDING_UP":
            if pattern in REVERSAL_PATTERNS["bearish_reversal"]:
                interpretations[pattern] = f"POTENTIAL REVERSAL - {pattern} in uptrend"
            else:
                interpretations[pattern] = f"Counter-trend signal - {pattern} (use caution)"
        elif market_regime == "TRENDING_DOWN":
            interpretations[pattern] = f"Trend continuation - {pattern} confirms downtrend"
        else:
            interpretations[pattern] = f"Bearish signal - {pattern}"
    
    return interpretations


def get_strongest_pattern(result: PatternResult) -> Optional[Dict[str, Any]]:
    """
    Get the strongest/most significant pattern detected.
    
    Strong patterns are multi-candle reversal patterns like:
    - Three White Soldiers / Three Black Crows
    - Morning Star / Evening Star
    - Engulfing patterns
    
    Returns:
        Dict with pattern name and direction, or None if no strong pattern
    """
    strong_bullish = [
        "CDL3WHITESOLDIERS", "CDLMORNINGSTAR", "CDLMORNINGDOJISTAR",
        "CDLENGULFING", "CDLABANDONEDBABY", "CDLKICKING"
    ]
    strong_bearish = [
        "CDL3BLACKCROWS", "CDLEVENINGSTAR", "CDLEVENINGDOJISTAR",
        "CDLENGULFING", "CDLABANDONEDBABY", "CDLKICKING"
    ]
    
    # Check for strong bullish patterns
    for pattern in strong_bullish:
        if pattern in result.bullish_patterns:
            return {"pattern": pattern, "direction": "BULLISH", "strength": "STRONG"}
    
    # Check for strong bearish patterns
    for pattern in strong_bearish:
        if pattern in result.bearish_patterns:
            return {"pattern": pattern, "direction": "BEARISH", "strength": "STRONG"}
    
    # Return any detected pattern as moderate
    if result.bullish_patterns:
        return {"pattern": result.bullish_patterns[0], "direction": "BULLISH", "strength": "MODERATE"}
    if result.bearish_patterns:
        return {"pattern": result.bearish_patterns[0], "direction": "BEARISH", "strength": "MODERATE"}
    
    return None
