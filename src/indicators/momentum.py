"""
Kuiper V2 - Momentum Indicators (31 Functions)
===============================================

All 31 TA-Lib Momentum functions with correct input requirements.

OFFICIAL TA-LIB SIGNATURES (from ta-lib.github.io):
----------------------------------------------------
CLOSE ONLY:
- APO(close, fastperiod=12, slowperiod=26, matype=0)
- CMO(close, timeperiod=14)  # unstable period
- MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)  # returns (macd, signal, hist)
- MACDEXT(close, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0)
- MACDFIX(close, signalperiod=9)
- MOM(close, timeperiod=10)
- PPO(close, fastperiod=12, slowperiod=26, matype=0)
- ROC(close, timeperiod=10)
- ROCP(close, timeperiod=10)
- ROCR(close, timeperiod=10)
- ROCR100(close, timeperiod=10)
- RSI(close, timeperiod=14)  # unstable period
- STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)  # unstable, returns (fastk, fastd)
- TRIX(close, timeperiod=30)

HIGH/LOW:
- AROON(high, low, timeperiod=14)  # returns (aroondown, aroonup)
- AROONOSC(high, low, timeperiod=14)
- MINUS_DM(high, low, timeperiod=14)  # unstable period
- PLUS_DM(high, low, timeperiod=14)  # unstable period

HIGH/LOW/CLOSE:
- ADX(high, low, close, timeperiod=14)  # unstable period
- ADXR(high, low, close, timeperiod=14)  # unstable period
- CCI(high, low, close, timeperiod=14)
- DX(high, low, close, timeperiod=14)  # unstable period
- MINUS_DI(high, low, close, timeperiod=14)  # unstable period
- PLUS_DI(high, low, close, timeperiod=14)  # unstable period
- STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)  # returns (slowk, slowd)
- STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0)  # returns (fastk, fastd)
- ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28)
- WILLR(high, low, close, timeperiod=14)

OPEN/HIGH/LOW/CLOSE:
- BOP(open, high, low, close)

OPEN/CLOSE:
- IMI(open, close, timeperiod=14)  # unstable period (Intraday Momentum Index)

HIGH/LOW/CLOSE/VOLUME:
- MFI(high, low, close, volume, timeperiod=14)  # unstable period
"""

import numpy as np
import talib
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MomentumResult:
    """Container for all momentum indicator results."""
    
    # RSI
    rsi_14: Optional[float] = None
    
    # MACD
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    
    # ADX Family
    adx_14: Optional[float] = None
    adxr_14: Optional[float] = None
    dx_14: Optional[float] = None
    plus_di_14: Optional[float] = None
    minus_di_14: Optional[float] = None
    plus_dm_14: Optional[float] = None
    minus_dm_14: Optional[float] = None
    
    # Stochastic
    stoch_slowk: Optional[float] = None
    stoch_slowd: Optional[float] = None
    stochf_fastk: Optional[float] = None
    stochf_fastd: Optional[float] = None
    stochrsi_fastk: Optional[float] = None
    stochrsi_fastd: Optional[float] = None
    
    # Aroon
    aroon_down: Optional[float] = None
    aroon_up: Optional[float] = None
    aroonosc: Optional[float] = None
    
    # CCI, CMO, MOM
    cci_14: Optional[float] = None
    cmo_14: Optional[float] = None
    mom_10: Optional[float] = None
    
    # Oscillators
    apo: Optional[float] = None
    ppo: Optional[float] = None
    bop: Optional[float] = None
    imi_14: Optional[float] = None
    
    # Rate of Change
    roc_10: Optional[float] = None
    rocp_10: Optional[float] = None
    rocr_10: Optional[float] = None
    rocr100_10: Optional[float] = None
    
    # Others
    trix_30: Optional[float] = None
    ultosc: Optional[float] = None
    willr_14: Optional[float] = None
    mfi_14: Optional[float] = None
    
    # Full arrays for analysis
    rsi_array: Optional[np.ndarray] = None
    macd_array: Optional[np.ndarray] = None
    adx_array: Optional[np.ndarray] = None


def compute_momentum(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> MomentumResult:
    """
    Compute all 31 Momentum indicators.
    
    Args:
        open_: Open prices (numpy array)
        high: High prices (numpy array)
        low: Low prices (numpy array)
        close: Close prices (numpy array)
        volume: Volume (numpy array)
    
    Returns:
        MomentumResult with all indicator values
    """
    result = MomentumResult()
    
    if len(close) < 30:
        return result  # Not enough data

    # =========================================================================
    # RSI - RELATIVE STRENGTH INDEX
    # Formula: RSI = 100 - (100 / (1 + RS))
    # RS = Average Gain / Average Loss over period
    # Interpretation:
    #   > 70: Overbought (in ranging markets)
    #   < 30: Oversold (in ranging markets)
    #   In trends: RSI can stay overbought/oversold for extended periods
    # NOTE: Has unstable period
    # =========================================================================
    try:
        rsi = talib.RSI(close, timeperiod=14)
        result.rsi_14 = _safe_last(rsi)
        result.rsi_array = rsi
    except Exception as e:
        print(f"RSI error: {e}")
    
    # =========================================================================
    # MACD - MOVING AVERAGE CONVERGENCE DIVERGENCE
    # MACD Line = EMA(12) - EMA(26)
    # Signal Line = EMA(9) of MACD Line
    # Histogram = MACD Line - Signal Line
    # Interpretation:
    #   MACD > Signal: Bullish momentum
    #   MACD < Signal: Bearish momentum
    #   Histogram expanding: Momentum increasing
    #   Histogram contracting: Momentum decreasing
    # =========================================================================
    try:
        macd, macd_signal, macd_hist = talib.MACD(
            close, 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        result.macd = _safe_last(macd)
        result.macd_signal = _safe_last(macd_signal)
        result.macd_hist = _safe_last(macd_hist)
        result.macd_array = macd
    except Exception as e:
        print(f"MACD error: {e}")
    
    # =========================================================================
    # ADX - AVERAGE DIRECTIONAL INDEX
    # Measures trend strength (not direction)
    # Formula: ADX = SMA(DX, period)
    # DX = |+DI - -DI| / (+DI + -DI) * 100
    # Interpretation:
    #   > 25: Strong trend
    #   20-25: Weak trend
    #   < 20: No trend (ranging)
    # NOTE: Has unstable period
    # =========================================================================
    try:
        adx = talib.ADX(high, low, close, timeperiod=14)
        result.adx_14 = _safe_last(adx)
        result.adx_array = adx
    except Exception as e:
        print(f"ADX error: {e}")
    
    # =========================================================================
    # ADXR - AVERAGE DIRECTIONAL MOVEMENT INDEX RATING
    # Smoothed version of ADX
    # Formula: ADXR = (ADX + ADX(n periods ago)) / 2
    # NOTE: Has unstable period
    # =========================================================================
    try:
        adxr = talib.ADXR(high, low, close, timeperiod=14)
        result.adxr_14 = _safe_last(adxr)
    except Exception as e:
        print(f"ADXR error: {e}")
    
    # =========================================================================
    # DX - DIRECTIONAL MOVEMENT INDEX
    # Raw directional movement before smoothing
    # Formula: DX = |+DI - -DI| / (+DI + -DI) * 100
    # NOTE: Has unstable period
    # =========================================================================
    try:
        dx = talib.DX(high, low, close, timeperiod=14)
        result.dx_14 = _safe_last(dx)
    except Exception as e:
        print(f"DX error: {e}")
    
    # =========================================================================
    # PLUS_DI - PLUS DIRECTIONAL INDICATOR
    # Measures upward price movement
    # Formula: +DI = 100 * SMA(+DM) / ATR
    # Interpretation: +DI > -DI suggests uptrend
    # NOTE: Has unstable period
    # =========================================================================
    try:
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
        result.plus_di_14 = _safe_last(plus_di)
    except Exception as e:
        print(f"PLUS_DI error: {e}")
    
    # =========================================================================
    # MINUS_DI - MINUS DIRECTIONAL INDICATOR
    # Measures downward price movement
    # Formula: -DI = 100 * SMA(-DM) / ATR
    # Interpretation: -DI > +DI suggests downtrend
    # NOTE: Has unstable period
    # =========================================================================
    try:
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
        result.minus_di_14 = _safe_last(minus_di)
    except Exception as e:
        print(f"MINUS_DI error: {e}")
    
    # =========================================================================
    # PLUS_DM - PLUS DIRECTIONAL MOVEMENT
    # Raw upward movement before normalization
    # Formula: +DM = High - Previous High (if positive and > -DM)
    # NOTE: Has unstable period
    # =========================================================================
    try:
        plus_dm = talib.PLUS_DM(high, low, timeperiod=14)
        result.plus_dm_14 = _safe_last(plus_dm)
    except Exception as e:
        print(f"PLUS_DM error: {e}")
    
    # =========================================================================
    # MINUS_DM - MINUS DIRECTIONAL MOVEMENT
    # Raw downward movement before normalization
    # Formula: -DM = Previous Low - Low (if positive and > +DM)
    # NOTE: Has unstable period
    # =========================================================================
    try:
        minus_dm = talib.MINUS_DM(high, low, timeperiod=14)
        result.minus_dm_14 = _safe_last(minus_dm)
    except Exception as e:
        print(f"MINUS_DM error: {e}")

    # =========================================================================
    # STOCH - STOCHASTIC OSCILLATOR (Slow)
    # Compares closing price to price range over period
    # %K = (Close - Lowest Low) / (Highest High - Lowest Low) * 100
    # Slow %K = SMA(%K, slowk_period)
    # Slow %D = SMA(Slow %K, slowd_period)
    # Interpretation:
    #   > 80: Overbought
    #   < 20: Oversold
    #   %K crossing %D: Signal
    # =========================================================================
    try:
        slowk, slowd = talib.STOCH(
            high, low, close,
            fastk_period=5,
            slowk_period=3,
            slowk_matype=0,  # SMA
            slowd_period=3,
            slowd_matype=0   # SMA
        )
        result.stoch_slowk = _safe_last(slowk)
        result.stoch_slowd = _safe_last(slowd)
    except Exception as e:
        print(f"STOCH error: {e}")
    
    # =========================================================================
    # STOCHF - STOCHASTIC FAST
    # Faster, more sensitive version
    # Fast %K = (Close - Lowest Low) / (Highest High - Lowest Low) * 100
    # Fast %D = SMA(Fast %K, fastd_period)
    # More responsive but noisier than slow stochastic
    # =========================================================================
    try:
        fastk, fastd = talib.STOCHF(
            high, low, close,
            fastk_period=5,
            fastd_period=3,
            fastd_matype=0  # SMA
        )
        result.stochf_fastk = _safe_last(fastk)
        result.stochf_fastd = _safe_last(fastd)
    except Exception as e:
        print(f"STOCHF error: {e}")
    
    # =========================================================================
    # STOCHRSI - STOCHASTIC RSI
    # Applies Stochastic formula to RSI values instead of price
    # StochRSI = (RSI - Lowest RSI) / (Highest RSI - Lowest RSI)
    # More sensitive than regular RSI
    # NOTE: Has unstable period
    # =========================================================================
    try:
        stochrsi_fastk, stochrsi_fastd = talib.STOCHRSI(
            close,
            timeperiod=14,
            fastk_period=5,
            fastd_period=3,
            fastd_matype=0  # SMA
        )
        result.stochrsi_fastk = _safe_last(stochrsi_fastk)
        result.stochrsi_fastd = _safe_last(stochrsi_fastd)
    except Exception as e:
        print(f"STOCHRSI error: {e}")
    
    # =========================================================================
    # AROON - AROON INDICATOR
    # Measures time since highest high and lowest low
    # Aroon Up = ((period - periods since highest high) / period) * 100
    # Aroon Down = ((period - periods since lowest low) / period) * 100
    # Interpretation:
    #   Aroon Up > 70 and Aroon Down < 30: Strong uptrend
    #   Aroon Down > 70 and Aroon Up < 30: Strong downtrend
    #   Both around 50: Consolidation
    # =========================================================================
    try:
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=14)
        result.aroon_down = _safe_last(aroon_down)
        result.aroon_up = _safe_last(aroon_up)
    except Exception as e:
        print(f"AROON error: {e}")
    
    # =========================================================================
    # AROONOSC - AROON OSCILLATOR
    # Difference between Aroon Up and Aroon Down
    # Formula: Aroon Oscillator = Aroon Up - Aroon Down
    # Interpretation:
    #   > 0: Bullish (uptrend)
    #   < 0: Bearish (downtrend)
    #   Magnitude indicates strength
    # =========================================================================
    try:
        aroonosc = talib.AROONOSC(high, low, timeperiod=14)
        result.aroonosc = _safe_last(aroonosc)
    except Exception as e:
        print(f"AROONOSC error: {e}")
    
    # =========================================================================
    # CCI - COMMODITY CHANNEL INDEX
    # Measures price deviation from statistical mean
    # Formula: CCI = (Typical Price - SMA(TP)) / (0.015 * Mean Deviation)
    # Typical Price = (High + Low + Close) / 3
    # Interpretation:
    #   > +100: Overbought / Strong uptrend
    #   < -100: Oversold / Strong downtrend
    #   Zero line crossovers: Trend changes
    # =========================================================================
    try:
        cci = talib.CCI(high, low, close, timeperiod=14)
        result.cci_14 = _safe_last(cci)
    except Exception as e:
        print(f"CCI error: {e}")
    
    # =========================================================================
    # CMO - CHANDE MOMENTUM OSCILLATOR
    # Similar to RSI but uses raw momentum
    # Formula: CMO = (Sum of Up Days - Sum of Down Days) / (Sum of Up Days + Sum of Down Days) * 100
    # Range: -100 to +100
    # Interpretation:
    #   > +50: Overbought
    #   < -50: Oversold
    # NOTE: Has unstable period
    # =========================================================================
    try:
        cmo = talib.CMO(close, timeperiod=14)
        result.cmo_14 = _safe_last(cmo)
    except Exception as e:
        print(f"CMO error: {e}")
    
    # =========================================================================
    # MOM - MOMENTUM
    # Simple price change over period
    # Formula: MOM = Close - Close(n periods ago)
    # Interpretation:
    #   > 0: Price higher than n periods ago (bullish)
    #   < 0: Price lower than n periods ago (bearish)
    #   Magnitude indicates strength
    # =========================================================================
    try:
        mom = talib.MOM(close, timeperiod=10)
        result.mom_10 = _safe_last(mom)
    except Exception as e:
        print(f"MOM error: {e}")

    # =========================================================================
    # APO - ABSOLUTE PRICE OSCILLATOR
    # Difference between two EMAs (absolute value)
    # Formula: APO = EMA(fast) - EMA(slow)
    # Similar to MACD but without signal line
    # Interpretation:
    #   > 0: Short-term momentum bullish
    #   < 0: Short-term momentum bearish
    # =========================================================================
    try:
        apo = talib.APO(close, fastperiod=12, slowperiod=26, matype=0)
        result.apo = _safe_last(apo)
    except Exception as e:
        print(f"APO error: {e}")
    
    # =========================================================================
    # PPO - PERCENTAGE PRICE OSCILLATOR
    # Percentage difference between two EMAs
    # Formula: PPO = ((EMA(fast) - EMA(slow)) / EMA(slow)) * 100
    # Normalized version of APO - comparable across different price levels
    # Interpretation:
    #   > 0: Bullish momentum
    #   < 0: Bearish momentum
    # =========================================================================
    try:
        ppo = talib.PPO(close, fastperiod=12, slowperiod=26, matype=0)
        result.ppo = _safe_last(ppo)
    except Exception as e:
        print(f"PPO error: {e}")
    
    # =========================================================================
    # BOP - BALANCE OF POWER
    # Measures strength of buyers vs sellers
    # Formula: BOP = (Close - Open) / (High - Low)
    # Range: -1 to +1
    # Interpretation:
    #   > 0: Buyers in control
    #   < 0: Sellers in control
    #   Near 0: Balanced
    # =========================================================================
    try:
        bop = talib.BOP(open_, high, low, close)
        result.bop = _safe_last(bop)
    except Exception as e:
        print(f"BOP error: {e}")
    
    # =========================================================================
    # IMI - INTRADAY MOMENTUM INDEX
    # RSI-like indicator using open-close relationship
    # Formula: IMI = (Sum of Gains) / (Sum of Gains + Sum of Losses) * 100
    # Gain = Close - Open (if Close > Open)
    # Loss = Open - Close (if Open > Close)
    # Interpretation:
    #   > 70: Overbought
    #   < 30: Oversold
    # NOTE: Has unstable period
    # =========================================================================
    try:
        # Note: TA-Lib doesn't have IMI directly, we compute it manually
        # IMI = 100 * sum(close-open when close>open) / sum(|close-open|)
        gains = np.where(close > open_, close - open_, 0)
        losses = np.where(close < open_, open_ - close, 0)
        
        period = 14
        if len(close) >= period:
            sum_gains = np.convolve(gains, np.ones(period), mode='valid')
            sum_losses = np.convolve(losses, np.ones(period), mode='valid')
            total = sum_gains + sum_losses
            imi = np.where(total > 0, 100 * sum_gains / total, 50)
            result.imi_14 = float(imi[-1]) if len(imi) > 0 else None
    except Exception as e:
        print(f"IMI error: {e}")
    
    # =========================================================================
    # ROC - RATE OF CHANGE
    # Percentage change over period
    # Formula: ROC = ((Close - Close(n)) / Close(n)) * 100
    # Interpretation:
    #   > 0: Price increased
    #   < 0: Price decreased
    #   Magnitude indicates rate of change
    # =========================================================================
    try:
        roc = talib.ROC(close, timeperiod=10)
        result.roc_10 = _safe_last(roc)
    except Exception as e:
        print(f"ROC error: {e}")
    
    # =========================================================================
    # ROCP - RATE OF CHANGE PERCENTAGE
    # Same as ROC but expressed as decimal
    # Formula: ROCP = (Close - Close(n)) / Close(n)
    # =========================================================================
    try:
        rocp = talib.ROCP(close, timeperiod=10)
        result.rocp_10 = _safe_last(rocp)
    except Exception as e:
        print(f"ROCP error: {e}")
    
    # =========================================================================
    # ROCR - RATE OF CHANGE RATIO
    # Ratio of current price to price n periods ago
    # Formula: ROCR = Close / Close(n)
    # Interpretation:
    #   > 1: Price increased
    #   < 1: Price decreased
    #   = 1: No change
    # =========================================================================
    try:
        rocr = talib.ROCR(close, timeperiod=10)
        result.rocr_10 = _safe_last(rocr)
    except Exception as e:
        print(f"ROCR error: {e}")
    
    # =========================================================================
    # ROCR100 - RATE OF CHANGE RATIO 100 SCALE
    # ROCR multiplied by 100
    # Formula: ROCR100 = (Close / Close(n)) * 100
    # Interpretation:
    #   > 100: Price increased
    #   < 100: Price decreased
    #   = 100: No change
    # =========================================================================
    try:
        rocr100 = talib.ROCR100(close, timeperiod=10)
        result.rocr100_10 = _safe_last(rocr100)
    except Exception as e:
        print(f"ROCR100 error: {e}")
    
    # =========================================================================
    # TRIX - TRIPLE SMOOTH EMA RATE OF CHANGE
    # 1-period ROC of triple-smoothed EMA
    # Formula: TRIX = ROC(EMA(EMA(EMA(Close))))
    # Very smooth, filters out noise
    # Interpretation:
    #   > 0: Bullish
    #   < 0: Bearish
    #   Zero line crossovers: Trend changes
    # =========================================================================
    try:
        trix = talib.TRIX(close, timeperiod=30)
        result.trix_30 = _safe_last(trix)
    except Exception as e:
        print(f"TRIX error: {e}")
    
    # =========================================================================
    # ULTOSC - ULTIMATE OSCILLATOR
    # Weighted average of three different timeframes
    # Formula: UO = 100 * ((4 * BP7/TR7) + (2 * BP14/TR14) + (BP28/TR28)) / 7
    # BP = Close - Min(Low, Previous Close)
    # TR = Max(High, Previous Close) - Min(Low, Previous Close)
    # Interpretation:
    #   > 70: Overbought
    #   < 30: Oversold
    #   Divergences are key signals
    # =========================================================================
    try:
        ultosc = talib.ULTOSC(
            high, low, close,
            timeperiod1=7,
            timeperiod2=14,
            timeperiod3=28
        )
        result.ultosc = _safe_last(ultosc)
    except Exception as e:
        print(f"ULTOSC error: {e}")
    
    # =========================================================================
    # WILLR - WILLIAMS %R
    # Similar to Stochastic but inverted scale
    # Formula: %R = (Highest High - Close) / (Highest High - Lowest Low) * -100
    # Range: -100 to 0
    # Interpretation:
    #   > -20: Overbought
    #   < -80: Oversold
    # =========================================================================
    try:
        willr = talib.WILLR(high, low, close, timeperiod=14)
        result.willr_14 = _safe_last(willr)
    except Exception as e:
        print(f"WILLR error: {e}")
    
    # =========================================================================
    # MFI - MONEY FLOW INDEX
    # Volume-weighted RSI
    # Formula: MFI = 100 - (100 / (1 + Money Flow Ratio))
    # Money Flow = Typical Price * Volume
    # Interpretation:
    #   > 80: Overbought
    #   < 20: Oversold
    #   Divergences with price are significant
    # NOTE: Has unstable period
    # =========================================================================
    try:
        mfi = talib.MFI(high, low, close, volume, timeperiod=14)
        result.mfi_14 = _safe_last(mfi)
    except Exception as e:
        print(f"MFI error: {e}")
    
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


def get_momentum_dict(result: MomentumResult) -> Dict[str, Any]:
    """Convert MomentumResult to dictionary for JSON output."""
    return {
        # RSI
        "RSI_14": result.rsi_14,
        
        # MACD
        "MACD": result.macd,
        "MACD_signal": result.macd_signal,
        "MACD_hist": result.macd_hist,
        
        # ADX Family
        "ADX_14": result.adx_14,
        "ADXR_14": result.adxr_14,
        "DX_14": result.dx_14,
        "PLUS_DI_14": result.plus_di_14,
        "MINUS_DI_14": result.minus_di_14,
        "PLUS_DM_14": result.plus_dm_14,
        "MINUS_DM_14": result.minus_dm_14,
        
        # Stochastic
        "STOCH_slowk": result.stoch_slowk,
        "STOCH_slowd": result.stoch_slowd,
        "STOCHF_fastk": result.stochf_fastk,
        "STOCHF_fastd": result.stochf_fastd,
        "STOCHRSI_fastk": result.stochrsi_fastk,
        "STOCHRSI_fastd": result.stochrsi_fastd,
        
        # Aroon
        "AROON_down": result.aroon_down,
        "AROON_up": result.aroon_up,
        "AROONOSC": result.aroonosc,
        
        # CCI, CMO, MOM
        "CCI_14": result.cci_14,
        "CMO_14": result.cmo_14,
        "MOM_10": result.mom_10,
        
        # Oscillators
        "APO": result.apo,
        "PPO": result.ppo,
        "BOP": result.bop,
        "IMI_14": result.imi_14,
        
        # Rate of Change
        "ROC_10": result.roc_10,
        "ROCP_10": result.rocp_10,
        "ROCR_10": result.rocr_10,
        "ROCR100_10": result.rocr100_10,
        
        # Others
        "TRIX_30": result.trix_30,
        "ULTOSC": result.ultosc,
        "WILLR_14": result.willr_14,
        "MFI_14": result.mfi_14,
    }
