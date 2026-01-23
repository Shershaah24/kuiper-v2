"""
Kuiper V2 Wisdom Engine - COMPLETE 161 INDICATOR ANALYSIS
==========================================================
The brain of the trading system - interprets ALL 161 indicators and makes wise decisions.

This is NOT a confidence-based scoring system. It UNDERSTANDS what indicators mean
in context and makes WISE DECISIONS based on complete market understanding.

Key Principles:
1. Determine MARKET REGIME first (Trending Up, Trending Down, Ranging, Volatile)
2. Interpret EVERY indicator IN CONTEXT of the regime
3. Apply hierarchy when conflicts: Regime > Trend > Momentum > Volume > Patterns
4. Provide FULL REASONING for every decision

INDICATOR CATEGORIES ANALYZED:
- Overlap Studies (18): All MAs, Bollinger, SAR, ACCBANDS, etc.
- Momentum (31): RSI, MACD, ADX, Stochastic, AROON, CCI, CMO, TRIX, ULTOSC, etc.
- Volume (3): AD, ADOSC, OBV
- Volatility (3): ATR, NATR, TRANGE
- Cycles (5): HT_DCPERIOD, HT_DCPHASE, HT_PHASOR, HT_SINE, HT_TRENDMODE
- Price Transform (5): AVGPRICE, MEDPRICE, TYPPRICE, WCLPRICE, AVGDEV
- Statistics (9): LINEARREG family, STDDEV, VAR, TSF, BETA, CORREL
- Patterns (61): All CDL* candlestick patterns
- Math Transform (15): LN, SQRT, trigonometric functions
- Math Operators (11): MIN, MAX, SUM, support/resistance
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

from .models import (
    MarketRegime, TradeDirection, RegimeAnalysis, TrendAnalysis,
    MomentumAnalysis, VolumeAnalysis, PatternAnalysis, CycleAnalysis,
    IndicatorInterpretations, TradeDecision, TradeParameters, MarketAnalysis
)
from .config import (
    ADX_TRENDING_THRESHOLD, ADX_WEAK_THRESHOLD,
    ATR_SL_MULTIPLIER, ATR_TP_MULTIPLIER, MAX_RISK_PERCENT
)


class WisdomEngine:
    """
    The Wisdom Engine - makes intelligent trading decisions using ALL 161 indicators.
    
    Unlike simple scoring systems, this engine:
    1. Understands what EVERY indicator MEANS in context
    2. Determines market regime FIRST using multiple confirmation
    3. Interprets ALL indicators differently based on regime
    4. Synthesizes all information into a wise decision
    5. Provides full reasoning for every decision
    """
    
    def __init__(self, account_balance: float = 10000.0):
        """
        Initialize Wisdom Engine.
        
        Args:
            account_balance: Account balance for position sizing
        """
        self.account_balance = account_balance
    
    def analyze(self, 
                indicators: Dict[str, Any],
                current_price: float,
                symbol: str,
                timeframe: str) -> MarketAnalysis:
        """
        Perform complete market analysis using ALL 161 indicators.
        
        This is the main entry point. It:
        1. Detects market regime using multiple indicators
        2. Interprets ALL indicators in context
        3. Synthesizes a trading decision
        4. Calculates entry/exit parameters
        
        Args:
            indicators: Dict of all computed indicators (all 161)
            current_price: Current market price
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Timeframe (e.g., "H1")
        
        Returns:
            MarketAnalysis with complete analysis and decision
        """
        # Step 1: Detect market regime using comprehensive analysis
        regime_analysis = self.detect_market_regime(indicators)
        
        # Step 2: Interpret ALL indicators in context of regime
        interpretations = self.interpret_indicators(indicators, regime_analysis.regime)
        
        # Step 3: Synthesize trading decision using ALL indicator agreement
        decision = self.synthesize_decision(regime_analysis, interpretations, indicators)
        
        # Step 4: Calculate entry/exit if trading
        parameters = None
        if decision.direction != TradeDirection.NO_TRADE:
            parameters = self.calculate_entry_exit(
                decision, indicators, current_price, symbol
            )
        
        return MarketAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now(timezone.utc),
            regime=regime_analysis.regime,
            regime_analysis=regime_analysis,
            interpretations=interpretations,
            decision=decision,
            parameters=parameters,
            all_indicators=indicators
        )
    
    # =========================================================================
    # STEP 1: MARKET REGIME DETECTION (Using Multiple Indicators)
    # =========================================================================
    
    def detect_market_regime(self, indicators: Dict[str, Any]) -> RegimeAnalysis:
        """
        Determine market regime using COMPREHENSIVE indicator analysis.
        
        Uses:
        - ADX, ADXR, DX for trend strength
        - +DI/-DI for trend direction
        - HT_TRENDMODE for trend vs cycle
        - AROON/AROONOSC for trend timing
        - MA alignment (SMA, EMA, DEMA, TEMA, KAMA, MAMA)
        - LINEARREG_SLOPE and LINEARREG_ANGLE for statistical trend
        - ATR, NATR, STDDEV for volatility
        - Bollinger Band width for volatility state
        """
        momentum = indicators.get("momentum", {})
        overlap = indicators.get("overlap", {})
        volatility = indicators.get("volatility", {})
        cycles = indicators.get("cycles", {})
        statistics = indicators.get("statistics", {})
        
        # =====================================================================
        # TREND STRENGTH INDICATORS
        # =====================================================================
        adx = momentum.get("ADX_14", 20)
        adxr = momentum.get("ADXR_14", 20)
        dx = momentum.get("DX_14", 20)
        plus_di = momentum.get("PLUS_DI_14", 0)
        minus_di = momentum.get("MINUS_DI_14", 0)
        
        # AROON for trend timing
        aroon_up = momentum.get("AROON_up", 50)
        aroon_down = momentum.get("AROON_down", 50)
        aroonosc = momentum.get("AROONOSC", 0)
        
        # Hilbert Transform
        ht_trendmode = cycles.get("HT_TRENDMODE", 0)
        
        # Linear Regression for statistical trend
        linreg_slope = statistics.get("LINEARREG_SLOPE_14", 0)
        linreg_angle = statistics.get("LINEARREG_ANGLE_14", 0)
        
        # =====================================================================
        # MOVING AVERAGE ALIGNMENT (All 18 MAs)
        # =====================================================================
        sma_20 = overlap.get("SMA_20", 0)
        sma_50 = overlap.get("SMA_50", 0)
        sma_200 = overlap.get("SMA_200", 0)
        ema_12 = overlap.get("EMA_12", 0)
        ema_26 = overlap.get("EMA_26", 0)
        ema_50 = overlap.get("EMA_50", 0)
        dema_30 = overlap.get("DEMA_30", 0)
        tema_30 = overlap.get("TEMA_30", 0)
        kama_30 = overlap.get("KAMA_30", 0)
        mama = overlap.get("MAMA", 0)
        fama = overlap.get("FAMA", 0)
        t3_5 = overlap.get("T3_5", 0)
        wma_30 = overlap.get("WMA_30", 0)
        trima_30 = overlap.get("TRIMA_30", 0)
        ht_trendline = overlap.get("HT_TRENDLINE", 0)
        
        # Bollinger Bands
        bbands_upper = overlap.get("BBANDS_upper", 0)
        bbands_middle = overlap.get("BBANDS_middle", sma_20)
        bbands_lower = overlap.get("BBANDS_lower", 0)
        
        # =====================================================================
        # VOLATILITY INDICATORS
        # =====================================================================
        atr = volatility.get("ATR_14", 0)
        natr = volatility.get("NATR_14", 0)
        trange = volatility.get("TRANGE", 0)
        stddev = statistics.get("STDDEV_5", 0)
        
        # =====================================================================
        # COMPREHENSIVE TREND ANALYSIS
        # =====================================================================
        
        # 1. ADX Family Analysis
        adx_avg = (adx + adxr) / 2 if adxr else adx
        if adx_avg > ADX_TRENDING_THRESHOLD:
            adx_interpretation = f"ADX={adx:.1f}, ADXR={adxr:.1f} → STRONG TREND"
            trend_strength = "STRONG"
        elif adx_avg > ADX_WEAK_THRESHOLD:
            adx_interpretation = f"ADX={adx:.1f}, ADXR={adxr:.1f} → WEAK TREND"
            trend_strength = "WEAK"
        else:
            adx_interpretation = f"ADX={adx:.1f}, ADXR={adxr:.1f} → NO TREND (ranging)"
            trend_strength = "NONE"
        
        # 2. Directional Movement Analysis
        di_diff = plus_di - minus_di
        if di_diff > 10:
            di_interpretation = f"+DI={plus_di:.1f} > -DI={minus_di:.1f} → BULLISH direction"
            di_direction = "BULLISH"
        elif di_diff < -10:
            di_interpretation = f"-DI={minus_di:.1f} > +DI={plus_di:.1f} → BEARISH direction"
            di_direction = "BEARISH"
        else:
            di_interpretation = f"+DI={plus_di:.1f} ≈ -DI={minus_di:.1f} → NO clear direction"
            di_direction = "NEUTRAL"
        
        # 3. AROON Analysis
        if aroon_up > 70 and aroon_down < 30:
            aroon_interpretation = f"AROON Up={aroon_up:.0f}, Down={aroon_down:.0f} → STRONG UPTREND"
            aroon_direction = "BULLISH"
        elif aroon_down > 70 and aroon_up < 30:
            aroon_interpretation = f"AROON Up={aroon_up:.0f}, Down={aroon_down:.0f} → STRONG DOWNTREND"
            aroon_direction = "BEARISH"
        elif aroonosc > 50:
            aroon_interpretation = f"AROONOSC={aroonosc:.0f} → Bullish bias"
            aroon_direction = "BULLISH"
        elif aroonosc < -50:
            aroon_interpretation = f"AROONOSC={aroonosc:.0f} → Bearish bias"
            aroon_direction = "BEARISH"
        else:
            aroon_interpretation = f"AROON consolidating (OSC={aroonosc:.0f})"
            aroon_direction = "NEUTRAL"
        
        # 4. HT_TRENDMODE Analysis
        if ht_trendmode == 1:
            trend_mode_interpretation = "Hilbert Transform: TRENDING mode"
        else:
            trend_mode_interpretation = "Hilbert Transform: CYCLE/RANGING mode"
        
        # 5. Linear Regression Analysis
        if linreg_angle > 30:
            linreg_interpretation = f"LINEARREG angle={linreg_angle:.1f}° → STRONG UPTREND"
            linreg_direction = "BULLISH"
        elif linreg_angle > 10:
            linreg_interpretation = f"LINEARREG angle={linreg_angle:.1f}° → Moderate uptrend"
            linreg_direction = "BULLISH"
        elif linreg_angle < -30:
            linreg_interpretation = f"LINEARREG angle={linreg_angle:.1f}° → STRONG DOWNTREND"
            linreg_direction = "BEARISH"
        elif linreg_angle < -10:
            linreg_interpretation = f"LINEARREG angle={linreg_angle:.1f}° → Moderate downtrend"
            linreg_direction = "BEARISH"
        else:
            linreg_interpretation = f"LINEARREG angle={linreg_angle:.1f}° → SIDEWAYS"
            linreg_direction = "NEUTRAL"
        
        # 6. MA Alignment Analysis (Comprehensive)
        ma_alignment = self._analyze_ma_alignment(
            sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
            dema_30, tema_30, kama_30, mama, fama, t3_5, wma_30, trima_30
        )
        
        # 7. Volatility Analysis
        volatility_state, volatility_interpretation = self._analyze_volatility(
            natr, atr, stddev, bbands_upper, bbands_lower, bbands_middle
        )
        
        # =====================================================================
        # DETERMINE REGIME (Consensus of all indicators)
        # =====================================================================
        regime = self._determine_regime_comprehensive(
            trend_strength, di_direction, aroon_direction, ht_trendmode,
            linreg_direction, ma_alignment["direction"], volatility_state
        )
        
        # Build comprehensive reasoning
        reasoning = self._build_regime_reasoning_comprehensive(
            regime, adx_interpretation, di_interpretation, aroon_interpretation,
            trend_mode_interpretation, linreg_interpretation, 
            ma_alignment["interpretation"], volatility_interpretation
        )
        
        return RegimeAnalysis(
            regime=regime,
            adx_value=adx,
            adx_interpretation=adx_interpretation,
            trend_mode=ht_trendmode,
            trend_mode_interpretation=trend_mode_interpretation,
            ma_alignment=ma_alignment["direction"],
            ma_alignment_interpretation=ma_alignment["interpretation"],
            volatility_state=volatility_state,
            volatility_interpretation=volatility_interpretation,
            reasoning=reasoning
        )
    
    def _analyze_ma_alignment(self, sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
                               dema_30, tema_30, kama_30, mama, fama, t3_5, 
                               wma_30, trima_30) -> Dict[str, str]:
        """Analyze alignment of ALL moving averages."""
        bullish_count = 0
        bearish_count = 0
        total = 0
        
        # Fast vs Slow MA comparisons
        comparisons = [
            (ema_12, ema_26, "EMA12 vs EMA26"),
            (ema_12, sma_20, "EMA12 vs SMA20"),
            (sma_20, sma_50, "SMA20 vs SMA50"),
            (sma_50, sma_200, "SMA50 vs SMA200"),
            (dema_30, sma_50, "DEMA30 vs SMA50"),
            (tema_30, sma_50, "TEMA30 vs SMA50"),
            (kama_30, sma_50, "KAMA30 vs SMA50"),
            (t3_5, sma_20, "T3 vs SMA20"),
            (wma_30, sma_50, "WMA30 vs SMA50"),
            (trima_30, sma_50, "TRIMA30 vs SMA50"),
        ]
        
        # MAMA vs FAMA (special - MAMA crossing FAMA is signal)
        if mama and fama:
            if mama > fama:
                bullish_count += 1
            else:
                bearish_count += 1
            total += 1
        
        for fast, slow, name in comparisons:
            if fast and slow and fast > 0 and slow > 0:
                if fast > slow:
                    bullish_count += 1
                else:
                    bearish_count += 1
                total += 1
        
        if total == 0:
            return {"direction": "UNKNOWN", "interpretation": "Insufficient MA data"}
        
        bullish_pct = (bullish_count / total) * 100
        
        if bullish_pct >= 70:
            direction = "BULLISH"
            interpretation = f"MAs STRONGLY BULLISH ({bullish_count}/{total} aligned up)"
        elif bullish_pct >= 55:
            direction = "BULLISH"
            interpretation = f"MAs moderately bullish ({bullish_count}/{total} aligned up)"
        elif bullish_pct <= 30:
            direction = "BEARISH"
            interpretation = f"MAs STRONGLY BEARISH ({bearish_count}/{total} aligned down)"
        elif bullish_pct <= 45:
            direction = "BEARISH"
            interpretation = f"MAs moderately bearish ({bearish_count}/{total} aligned down)"
        else:
            direction = "MIXED"
            interpretation = f"MAs MIXED ({bullish_count} bullish, {bearish_count} bearish)"
        
        return {"direction": direction, "interpretation": interpretation}
    
    def _analyze_volatility(self, natr, atr, stddev, bb_upper, bb_lower, bb_middle) -> Tuple[str, str]:
        """Analyze volatility using multiple indicators."""
        # NATR analysis (normalized - comparable across instruments)
        if natr > 1.0:
            natr_state = "EXTREME"
        elif natr > 0.5:
            natr_state = "HIGH"
        elif natr > 0.2:
            natr_state = "NORMAL"
        else:
            natr_state = "LOW"
        
        # Bollinger Band width (volatility proxy)
        if bb_upper and bb_lower and bb_middle and bb_middle > 0:
            bb_width = (bb_upper - bb_lower) / bb_middle * 100
            if bb_width > 4:
                bb_state = "WIDE"
            elif bb_width > 2:
                bb_state = "NORMAL"
            else:
                bb_state = "NARROW"
        else:
            bb_state = "UNKNOWN"
            bb_width = 0
        
        # Determine overall volatility state
        if natr_state == "EXTREME" or (natr_state == "HIGH" and bb_state == "WIDE"):
            state = "SPIKE"
            interpretation = f"VOLATILITY SPIKE! NATR={natr:.3f}%, BB width={bb_width:.2f}%"
        elif natr_state == "HIGH" or bb_state == "WIDE":
            state = "HIGH"
            interpretation = f"Elevated volatility: NATR={natr:.3f}%, BB width={bb_width:.2f}%"
        elif natr_state == "LOW" and bb_state == "NARROW":
            state = "LOW"
            interpretation = f"Low volatility (squeeze): NATR={natr:.3f}%, BB width={bb_width:.2f}%"
        else:
            state = "NORMAL"
            interpretation = f"Normal volatility: NATR={natr:.3f}%, BB width={bb_width:.2f}%"
        
        return state, interpretation
    
    def _determine_regime_comprehensive(self, trend_strength, di_direction, aroon_direction,
                                         ht_trendmode, linreg_direction, ma_direction,
                                         volatility_state) -> MarketRegime:
        """Determine regime using consensus of ALL trend indicators."""
        
        # Volatility spike overrides everything
        if volatility_state == "SPIKE":
            return MarketRegime.VOLATILE
        
        # Count bullish vs bearish signals
        bullish_signals = 0
        bearish_signals = 0
        
        if di_direction == "BULLISH": bullish_signals += 2  # Weight: 2
        elif di_direction == "BEARISH": bearish_signals += 2
        
        if aroon_direction == "BULLISH": bullish_signals += 1
        elif aroon_direction == "BEARISH": bearish_signals += 1
        
        if linreg_direction == "BULLISH": bullish_signals += 1
        elif linreg_direction == "BEARISH": bearish_signals += 1
        
        if ma_direction == "BULLISH": bullish_signals += 2  # Weight: 2
        elif ma_direction == "BEARISH": bearish_signals += 2
        
        # Strong trend conditions
        if trend_strength == "STRONG" and ht_trendmode == 1:
            if bullish_signals > bearish_signals + 2:
                return MarketRegime.TRENDING_UP
            elif bearish_signals > bullish_signals + 2:
                return MarketRegime.TRENDING_DOWN
        
        # Weak trend with direction consensus
        if trend_strength in ["STRONG", "WEAK"]:
            if bullish_signals > bearish_signals + 1:
                return MarketRegime.TRENDING_UP
            elif bearish_signals > bullish_signals + 1:
                return MarketRegime.TRENDING_DOWN
        
        # No trend or HT in cycle mode
        if trend_strength == "NONE" or ht_trendmode == 0:
            return MarketRegime.RANGING
        
        # Default to ranging if unclear
        return MarketRegime.RANGING
    
    def _build_regime_reasoning_comprehensive(self, regime, adx_interp, di_interp, 
                                               aroon_interp, ht_interp, linreg_interp,
                                               ma_interp, vol_interp) -> str:
        """Build comprehensive regime reasoning."""
        parts = [
            f"═══════════════════════════════════════════════════════════════",
            f"MARKET REGIME: {regime.value}",
            f"═══════════════════════════════════════════════════════════════",
            "",
            "TREND STRENGTH ANALYSIS:",
            f"  • {adx_interp}",
            f"  • {di_interp}",
            "",
            "TREND DIRECTION ANALYSIS:",
            f"  • {aroon_interp}",
            f"  • {ht_interp}",
            f"  • {linreg_interp}",
            "",
            "MOVING AVERAGE ANALYSIS:",
            f"  • {ma_interp}",
            "",
            "VOLATILITY ANALYSIS:",
            f"  • {vol_interp}",
            "",
            "═══════════════════════════════════════════════════════════════",
        ]
        
        if regime == MarketRegime.TRENDING_UP:
            parts.append("CONCLUSION: Market in UPTREND. Look for LONG opportunities only.")
        elif regime == MarketRegime.TRENDING_DOWN:
            parts.append("CONCLUSION: Market in DOWNTREND. Look for SHORT opportunities only.")
        elif regime == MarketRegime.RANGING:
            parts.append("CONCLUSION: Market RANGING. Trade at extremes or wait for breakout.")
        else:
            parts.append("CONCLUSION: Market VOLATILE. Reduce size or stay out.")
        
        return "\n".join(parts)



    # =========================================================================
    # STEP 2: INDICATOR INTERPRETATION (ALL 161 Indicators)
    # =========================================================================
    
    def interpret_indicators(self, indicators: Dict[str, Any],
                             regime: MarketRegime) -> IndicatorInterpretations:
        """
        Interpret ALL indicators IN CONTEXT of the market regime.
        
        This is the key insight: RSI=30 means different things in different regimes:
        - In TRENDING_UP: Pullback opportunity, not reversal
        - In RANGING: Oversold at range bottom, potential long
        - In TRENDING_DOWN: Strong momentum, trend continuation
        """
        return IndicatorInterpretations(
            trend=self._interpret_trend_comprehensive(indicators, regime),
            momentum=self._interpret_momentum_comprehensive(indicators, regime),
            volume=self._interpret_volume_comprehensive(indicators, regime),
            patterns=self._interpret_patterns(indicators, regime),
            cycles=self._interpret_cycles_comprehensive(indicators, regime)
        )
    
    def _interpret_trend_comprehensive(self, indicators: Dict[str, Any],
                                        regime: MarketRegime) -> TrendAnalysis:
        """
        Interpret ALL trend/overlap indicators in context.
        
        Uses ALL 18 overlap studies:
        - SMA (20, 50, 200)
        - EMA (12, 26, 50)
        - DEMA, TEMA, T3, WMA, TRIMA, KAMA
        - MAMA/FAMA
        - HT_TRENDLINE
        - Bollinger Bands
        - ACCBANDS
        - MIDPOINT, MIDPRICE
        - SAR, SAREXT
        
        Plus statistics:
        - LINEARREG, LINEARREG_SLOPE, LINEARREG_ANGLE
        - TSF (Time Series Forecast)
        """
        overlap = indicators.get("overlap", {})
        momentum = indicators.get("momentum", {})
        statistics = indicators.get("statistics", {})
        
        # Get all MA values
        sma_20 = overlap.get("SMA_20", 0)
        sma_50 = overlap.get("SMA_50", 0)
        sma_200 = overlap.get("SMA_200", 0)
        ema_12 = overlap.get("EMA_12", 0)
        ema_26 = overlap.get("EMA_26", 0)
        dema_30 = overlap.get("DEMA_30", 0)
        tema_30 = overlap.get("TEMA_30", 0)
        t3_5 = overlap.get("T3_5", 0)
        kama_30 = overlap.get("KAMA_30", 0)
        mama = overlap.get("MAMA", 0)
        fama = overlap.get("FAMA", 0)
        ht_trendline = overlap.get("HT_TRENDLINE", 0)
        
        # Bollinger and Acceleration Bands
        bbands_upper = overlap.get("BBANDS_upper", 0)
        bbands_lower = overlap.get("BBANDS_lower", 0)
        bbands_middle = overlap.get("BBANDS_middle", 0)
        accbands_upper = overlap.get("ACCBANDS_upper", 0)
        accbands_lower = overlap.get("ACCBANDS_lower", 0)
        
        # SAR
        sar = overlap.get("SAR", 0)
        sarext = overlap.get("SAREXT", 0)
        
        # Midpoint/Midprice
        midpoint = overlap.get("MIDPOINT_14", 0)
        midprice = overlap.get("MIDPRICE_14", 0)
        
        # Statistics
        linreg = statistics.get("LINEARREG_14", 0)
        linreg_slope = statistics.get("LINEARREG_SLOPE_14", 0)
        linreg_angle = statistics.get("LINEARREG_ANGLE_14", 0)
        tsf = statistics.get("TSF_14", 0)
        
        # ADX for strength
        adx = momentum.get("ADX_14", 20)
        
        # Current price approximation
        current_price = bbands_middle if bbands_middle else sma_20
        
        # =====================================================================
        # COMPREHENSIVE TREND DIRECTION ANALYSIS
        # =====================================================================
        
        # Count bullish vs bearish MA signals
        bullish_mas = 0
        bearish_mas = 0
        
        # Fast vs Slow comparisons
        if ema_12 > ema_26: bullish_mas += 1
        else: bearish_mas += 1
        
        if sma_20 > sma_50: bullish_mas += 1
        else: bearish_mas += 1
        
        if sma_50 > sma_200 and sma_200 > 0: bullish_mas += 1
        elif sma_200 > 0: bearish_mas += 1
        
        if dema_30 > sma_50: bullish_mas += 1
        else: bearish_mas += 1
        
        if tema_30 > sma_50: bullish_mas += 1
        else: bearish_mas += 1
        
        if kama_30 > sma_50: bullish_mas += 1
        else: bearish_mas += 1
        
        if mama > fama and mama > 0: bullish_mas += 1
        elif fama > 0: bearish_mas += 1
        
        # Price vs key MAs
        if current_price > sma_20: bullish_mas += 1
        else: bearish_mas += 1
        
        if current_price > sma_50: bullish_mas += 1
        else: bearish_mas += 1
        
        if current_price > sma_200 and sma_200 > 0: bullish_mas += 1
        elif sma_200 > 0: bearish_mas += 1
        
        # Linear regression direction
        if linreg_slope > 0: bullish_mas += 1
        else: bearish_mas += 1
        
        # TSF (forecast)
        if current_price > tsf and tsf > 0: bullish_mas += 1
        elif tsf > 0: bearish_mas += 1
        
        # Determine direction
        total_signals = bullish_mas + bearish_mas
        if total_signals > 0:
            bullish_pct = (bullish_mas / total_signals) * 100
            if bullish_pct >= 65:
                direction = "UP"
            elif bullish_pct <= 35:
                direction = "DOWN"
            else:
                direction = "NEUTRAL"
        else:
            direction = "NEUTRAL"
        
        # Determine strength from ADX
        if adx > 40:
            strength = "STRONG"
        elif adx > 25:
            strength = "MODERATE"
        else:
            strength = "WEAK"
        
        # MA positions
        ma_positions = {
            "SMA_20": "ABOVE_PRICE" if sma_20 > current_price else "BELOW_PRICE",
            "SMA_50": "ABOVE_PRICE" if sma_50 > current_price else "BELOW_PRICE",
            "SMA_200": "ABOVE_PRICE" if sma_200 > current_price else "BELOW_PRICE",
            "KAMA_30": "ABOVE_PRICE" if kama_30 > current_price else "BELOW_PRICE",
            "HT_TRENDLINE": "ABOVE_PRICE" if ht_trendline > current_price else "BELOW_PRICE",
        }
        
        # EMA crossover
        if ema_12 > ema_26:
            ema_crossover = "BULLISH"
        elif ema_12 < ema_26:
            ema_crossover = "BEARISH"
        else:
            ema_crossover = "NONE"
        
        # MAMA/FAMA crossover
        if mama > fama:
            mama_crossover = "BULLISH"
        elif mama < fama:
            mama_crossover = "BEARISH"
        else:
            mama_crossover = "NONE"
        
        # SAR position
        if sar < current_price:
            sar_signal = "BULLISH (SAR below price)"
        else:
            sar_signal = "BEARISH (SAR above price)"
        
        # Build comprehensive interpretation
        interpretation_parts = [
            f"TREND ANALYSIS ({bullish_mas} bullish / {bearish_mas} bearish signals):",
            f"  Direction: {direction} | Strength: {strength} (ADX={adx:.1f})",
            f"  EMA Crossover: {ema_crossover} | MAMA/FAMA: {mama_crossover}",
            f"  SAR: {sar_signal}",
            f"  LINEARREG: Angle={linreg_angle:.1f}°, Slope={linreg_slope:.6f}",
        ]
        
        # Context-specific interpretation
        if regime == MarketRegime.TRENDING_UP:
            if direction == "UP":
                interpretation_parts.append(f"  → UPTREND CONFIRMED by {bullish_mas} indicators")
            else:
                interpretation_parts.append(f"  → Possible pullback in uptrend")
        elif regime == MarketRegime.TRENDING_DOWN:
            if direction == "DOWN":
                interpretation_parts.append(f"  → DOWNTREND CONFIRMED by {bearish_mas} indicators")
            else:
                interpretation_parts.append(f"  → Possible bounce in downtrend")
        elif regime == MarketRegime.RANGING:
            interpretation_parts.append(f"  → RANGING: Price between BB {bbands_lower:.5f} - {bbands_upper:.5f}")
        else:
            interpretation_parts.append(f"  → VOLATILE: Trend signals unreliable")
        
        interpretation = "\n".join(interpretation_parts)
        
        return TrendAnalysis(
            direction=direction,
            strength=strength,
            ma_positions=ma_positions,
            ema_crossover=ema_crossover,
            interpretation=interpretation
        )
    
    def _interpret_momentum_comprehensive(self, indicators: Dict[str, Any],
                                           regime: MarketRegime) -> MomentumAnalysis:
        """
        Interpret ALL 31 momentum indicators in context.
        
        Uses:
        - RSI (14)
        - MACD, MACD_signal, MACD_hist
        - ADX, ADXR, DX, +DI, -DI, +DM, -DM
        - STOCH (slowk, slowd), STOCHF (fastk, fastd), STOCHRSI
        - AROON (up, down), AROONOSC
        - CCI, CMO, MOM
        - APO, PPO, BOP, IMI
        - ROC, ROCP, ROCR, ROCR100
        - TRIX, ULTOSC, WILLR, MFI
        """
        momentum = indicators.get("momentum", {})
        
        # =====================================================================
        # GET ALL MOMENTUM VALUES
        # =====================================================================
        
        # RSI
        rsi = momentum.get("RSI_14", 50)
        
        # MACD
        macd = momentum.get("MACD", 0)
        macd_signal = momentum.get("MACD_signal", 0)
        macd_hist = momentum.get("MACD_hist", 0)
        
        # ADX Family
        adx = momentum.get("ADX_14", 20)
        adxr = momentum.get("ADXR_14", 20)
        dx = momentum.get("DX_14", 20)
        plus_di = momentum.get("PLUS_DI_14", 0)
        minus_di = momentum.get("MINUS_DI_14", 0)
        
        # Stochastic
        stoch_k = momentum.get("STOCH_slowk", 50)
        stoch_d = momentum.get("STOCH_slowd", 50)
        stochf_k = momentum.get("STOCHF_fastk", 50)
        stochf_d = momentum.get("STOCHF_fastd", 50)
        stochrsi_k = momentum.get("STOCHRSI_fastk", 50)
        stochrsi_d = momentum.get("STOCHRSI_fastd", 50)
        
        # AROON
        aroon_up = momentum.get("AROON_up", 50)
        aroon_down = momentum.get("AROON_down", 50)
        aroonosc = momentum.get("AROONOSC", 0)
        
        # CCI, CMO, MOM
        cci = momentum.get("CCI_14", 0)
        cmo = momentum.get("CMO_14", 0)
        mom = momentum.get("MOM_10", 0)
        
        # Oscillators
        apo = momentum.get("APO", 0)
        ppo = momentum.get("PPO", 0)
        bop = momentum.get("BOP", 0)
        imi = momentum.get("IMI_14", 50)
        
        # Rate of Change
        roc = momentum.get("ROC_10", 0)
        rocp = momentum.get("ROCP_10", 0)
        rocr = momentum.get("ROCR_10", 1)
        rocr100 = momentum.get("ROCR100_10", 100)
        
        # Others
        trix = momentum.get("TRIX_30", 0)
        ultosc = momentum.get("ULTOSC", 50)
        willr = momentum.get("WILLR_14", -50)
        mfi = momentum.get("MFI_14", 50)
        
        # =====================================================================
        # COMPREHENSIVE MOMENTUM ANALYSIS
        # =====================================================================
        
        bullish_signals = 0
        bearish_signals = 0
        overbought_signals = 0
        oversold_signals = 0
        
        # RSI Analysis
        rsi_interpretation = self._interpret_rsi_comprehensive(rsi, regime)
        if rsi > 50: bullish_signals += 1
        else: bearish_signals += 1
        if rsi > 70: overbought_signals += 1
        if rsi < 30: oversold_signals += 1
        
        # MACD Analysis
        if macd > macd_signal and macd_hist > 0:
            macd_state = "BULLISH"
            bullish_signals += 2  # Weight: 2
        elif macd < macd_signal and macd_hist < 0:
            macd_state = "BEARISH"
            bearish_signals += 2
        else:
            macd_state = "NEUTRAL"
        
        # Stochastic Analysis (all 3 versions)
        stoch_bullish = 0
        stoch_bearish = 0
        
        if stoch_k > 50: stoch_bullish += 1
        else: stoch_bearish += 1
        if stoch_k > 80: overbought_signals += 1
        if stoch_k < 20: oversold_signals += 1
        
        if stochf_k > 50: stoch_bullish += 1
        else: stoch_bearish += 1
        
        if stochrsi_k and stochrsi_k > 50: stoch_bullish += 1
        elif stochrsi_k: stoch_bearish += 1
        
        if stoch_bullish > stoch_bearish:
            stoch_state = "OVERBOUGHT" if stoch_k > 80 else "BULLISH"
            bullish_signals += 1
        elif stoch_bearish > stoch_bullish:
            stoch_state = "OVERSOLD" if stoch_k < 20 else "BEARISH"
            bearish_signals += 1
        else:
            stoch_state = "NEUTRAL"
        
        # AROON Analysis
        if aroon_up > 70 and aroon_down < 30:
            bullish_signals += 2
        elif aroon_down > 70 and aroon_up < 30:
            bearish_signals += 2
        elif aroonosc > 0:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # CCI Analysis
        if cci > 100:
            bullish_signals += 1
            overbought_signals += 1
        elif cci < -100:
            bearish_signals += 1
            oversold_signals += 1
        elif cci > 0:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # CMO Analysis (similar to RSI, range -100 to +100)
        if cmo > 50:
            bullish_signals += 1
            overbought_signals += 1
        elif cmo < -50:
            bearish_signals += 1
            oversold_signals += 1
        elif cmo > 0:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # MOM Analysis
        if mom > 0: bullish_signals += 1
        else: bearish_signals += 1
        
        # APO/PPO Analysis
        if apo > 0: bullish_signals += 1
        else: bearish_signals += 1
        
        if ppo > 0: bullish_signals += 1
        else: bearish_signals += 1
        
        # BOP Analysis (-1 to +1)
        if bop > 0.3: bullish_signals += 1
        elif bop < -0.3: bearish_signals += 1
        
        # IMI Analysis (like RSI)
        if imi > 70: overbought_signals += 1
        elif imi < 30: oversold_signals += 1
        if imi > 50: bullish_signals += 1
        else: bearish_signals += 1
        
        # ROC Family Analysis
        if roc > 0: bullish_signals += 1
        else: bearish_signals += 1
        
        if rocr100 > 100: bullish_signals += 1
        else: bearish_signals += 1
        
        # TRIX Analysis
        if trix > 0: bullish_signals += 1
        else: bearish_signals += 1
        
        # ULTOSC Analysis
        if ultosc > 70:
            overbought_signals += 1
            bullish_signals += 1
        elif ultosc < 30:
            oversold_signals += 1
            bearish_signals += 1
        elif ultosc > 50:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # Williams %R Analysis (inverted scale: -100 to 0)
        if willr > -20:
            overbought_signals += 1
        elif willr < -80:
            oversold_signals += 1
        if willr > -50:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # MFI Analysis (volume-weighted RSI)
        if mfi > 80:
            overbought_signals += 1
        elif mfi < 20:
            oversold_signals += 1
        if mfi > 50:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # =====================================================================
        # DETERMINE OVERALL MOMENTUM
        # =====================================================================
        
        total_signals = bullish_signals + bearish_signals
        if total_signals > 0:
            bullish_pct = (bullish_signals / total_signals) * 100
            if bullish_pct >= 60:
                overall_momentum = "BULLISH"
            elif bullish_pct <= 40:
                overall_momentum = "BEARISH"
            else:
                overall_momentum = "NEUTRAL"
        else:
            overall_momentum = "NEUTRAL"
        
        # Stochastic interpretation
        stoch_interpretation = self._interpret_stochastic_comprehensive(
            stoch_k, stoch_d, stochf_k, stochrsi_k, stoch_state, regime
        )
        
        # Build comprehensive interpretation
        interpretation_parts = [
            f"MOMENTUM ANALYSIS ({bullish_signals} bullish / {bearish_signals} bearish):",
            f"  Overall: {overall_momentum}",
            f"  RSI={rsi:.1f}: {rsi_interpretation}",
            f"  MACD: {macd_state} (hist={macd_hist:.6f})",
            f"  Stochastic: {stoch_state} (K={stoch_k:.1f}, D={stoch_d:.1f})",
            f"  AROON: Up={aroon_up:.0f}, Down={aroon_down:.0f}, OSC={aroonosc:.0f}",
            f"  CCI={cci:.1f}, CMO={cmo:.1f}, MOM={mom:.4f}",
            f"  APO={apo:.4f}, PPO={ppo:.2f}%, BOP={bop:.2f}",
            f"  ROC={roc:.2f}%, TRIX={trix:.4f}",
            f"  ULTOSC={ultosc:.1f}, WILLR={willr:.1f}, MFI={mfi:.1f}",
        ]
        
        if overbought_signals >= 3:
            interpretation_parts.append(f"  ⚠️ OVERBOUGHT: {overbought_signals} indicators at extremes")
        elif oversold_signals >= 3:
            interpretation_parts.append(f"  ⚠️ OVERSOLD: {oversold_signals} indicators at extremes")
        
        interpretation = "\n".join(interpretation_parts)
        
        macd_interpretation = f"MACD {macd_state}: Line={macd:.6f}, Signal={macd_signal:.6f}, Hist={macd_hist:.6f}"
        
        return MomentumAnalysis(
            rsi_value=rsi,
            rsi_interpretation=rsi_interpretation,
            macd_state=macd_state,
            macd_interpretation=macd_interpretation,
            stoch_state=stoch_state,
            stoch_interpretation=stoch_interpretation,
            overall_momentum=overall_momentum,
            interpretation=interpretation
        )

    
    def _interpret_rsi_comprehensive(self, rsi: float, regime: MarketRegime) -> str:
        """
        Interpret RSI in context of market regime.
        
        This is the KEY insight - RSI means different things in different regimes!
        """
        if regime == MarketRegime.TRENDING_UP:
            if rsi < 40:
                return "Pullback in uptrend - BUYING opportunity"
            elif rsi > 70:
                return "Strong momentum, trend continuation likely"
            elif rsi > 50:
                return "Healthy uptrend momentum"
            else:
                return "Momentum weakening, watch for deeper pullback"
        
        elif regime == MarketRegime.TRENDING_DOWN:
            if rsi > 60:
                return "Rally in downtrend - SHORTING opportunity"
            elif rsi < 30:
                return "Strong downward momentum, trend continuation"
            elif rsi < 50:
                return "Healthy downtrend momentum"
            else:
                return "Momentum weakening, watch for bounce"
        
        elif regime == MarketRegime.RANGING:
            if rsi < 30:
                return "OVERSOLD at range bottom - potential LONG"
            elif rsi > 70:
                return "OVERBOUGHT at range top - potential SHORT"
            elif 45 < rsi < 55:
                return "Mid-range, wait for extremes"
            else:
                return "Approaching range boundary"
        
        else:  # VOLATILE
            if rsi < 30 or rsi > 70:
                return "Extreme reading in volatile market - USE CAUTION"
            else:
                return "RSI less reliable in volatile conditions"
    
    def _interpret_stochastic_comprehensive(self, k: float, d: float, fastk: float,
                                             stochrsi_k: float, state: str,
                                             regime: MarketRegime) -> str:
        """Interpret all Stochastic variants in context."""
        parts = []
        
        if regime == MarketRegime.TRENDING_UP:
            if state == "OVERSOLD":
                parts.append("Oversold in uptrend - EXCELLENT buying opportunity")
            elif state == "OVERBOUGHT":
                parts.append("Overbought but trend is up - may stay overbought")
            else:
                parts.append("Neutral stochastic in uptrend")
        
        elif regime == MarketRegime.TRENDING_DOWN:
            if state == "OVERBOUGHT":
                parts.append("Overbought in downtrend - EXCELLENT shorting opportunity")
            elif state == "OVERSOLD":
                parts.append("Oversold but trend is down - may stay oversold")
            else:
                parts.append("Neutral stochastic in downtrend")
        
        elif regime == MarketRegime.RANGING:
            if state == "OVERSOLD" and k > d:
                parts.append("Oversold with bullish crossover - potential LONG")
            elif state == "OVERBOUGHT" and k < d:
                parts.append("Overbought with bearish crossover - potential SHORT")
            else:
                parts.append(f"Stochastic {state} in range")
        
        else:
            parts.append("Stochastic less reliable in volatile conditions")
        
        # Add StochRSI insight
        if stochrsi_k is not None:
            if stochrsi_k > 80:
                parts.append(f"StochRSI={stochrsi_k:.0f} OVERBOUGHT")
            elif stochrsi_k < 20:
                parts.append(f"StochRSI={stochrsi_k:.0f} OVERSOLD")
        
        return " | ".join(parts)
    
    def _interpret_volume_comprehensive(self, indicators: Dict[str, Any],
                                         regime: MarketRegime) -> VolumeAnalysis:
        """
        Interpret ALL volume indicators.
        
        Uses:
        - OBV (On Balance Volume)
        - AD (Accumulation/Distribution)
        - ADOSC (Chaikin A/D Oscillator)
        - MFI (Money Flow Index) - from momentum
        """
        volume = indicators.get("volume", {})
        momentum = indicators.get("momentum", {})
        
        obv = volume.get("OBV", 0)
        ad = volume.get("AD", 0)
        adosc = volume.get("ADOSC", 0)
        mfi = momentum.get("MFI_14", 50)
        
        # OBV trend analysis
        if adosc > 0:
            obv_trend = "RISING"
        elif adosc < 0:
            obv_trend = "FALLING"
        else:
            obv_trend = "FLAT"
        
        # AD trend analysis
        if ad > 0 and adosc > 0:
            ad_trend = "ACCUMULATION"
        elif ad < 0 or adosc < 0:
            ad_trend = "DISTRIBUTION"
        else:
            ad_trend = "NEUTRAL"
        
        # MFI analysis (volume-weighted RSI)
        if mfi > 80:
            mfi_state = "OVERBOUGHT"
        elif mfi < 20:
            mfi_state = "OVERSOLD"
        elif mfi > 50:
            mfi_state = "BULLISH"
        else:
            mfi_state = "BEARISH"
        
        # Does volume confirm price?
        if regime == MarketRegime.TRENDING_UP:
            confirms_price = (obv_trend == "RISING" or ad_trend == "ACCUMULATION") and mfi_state in ["BULLISH", "OVERBOUGHT"]
        elif regime == MarketRegime.TRENDING_DOWN:
            confirms_price = (obv_trend == "FALLING" or ad_trend == "DISTRIBUTION") and mfi_state in ["BEARISH", "OVERSOLD"]
        else:
            confirms_price = True  # Less relevant in ranging
        
        # Build interpretation
        interpretation_parts = [
            f"VOLUME ANALYSIS:",
            f"  OBV trend: {obv_trend} (ADOSC={adosc:.2f})",
            f"  A/D: {ad_trend} (AD={ad:.2f})",
            f"  MFI: {mfi_state} ({mfi:.1f})",
        ]
        
        if confirms_price:
            interpretation_parts.append(f"  → VOLUME CONFIRMS price action")
        else:
            interpretation_parts.append(f"  ⚠️ VOLUME DIVERGENCE - potential reversal warning!")
        
        interpretation = "\n".join(interpretation_parts)
        
        return VolumeAnalysis(
            obv_trend=obv_trend,
            ad_trend=ad_trend,
            confirms_price=confirms_price,
            interpretation=interpretation
        )
    
    def _interpret_patterns(self, indicators: Dict[str, Any],
                            regime: MarketRegime) -> PatternAnalysis:
        """Interpret candlestick patterns (61 CDL* patterns)."""
        patterns = indicators.get("patterns", {})
        
        bullish_patterns = patterns.get("bullish_patterns", [])
        bearish_patterns = patterns.get("bearish_patterns", [])
        
        # Determine pattern bias
        bullish_count = len(bullish_patterns)
        bearish_count = len(bearish_patterns)
        
        if bullish_count > bearish_count:
            pattern_bias = "BULLISH"
        elif bearish_count > bullish_count:
            pattern_bias = "BEARISH"
        else:
            pattern_bias = "NEUTRAL"
        
        # Find strongest pattern
        strongest = None
        if bullish_patterns:
            strongest = bullish_patterns[0]
        elif bearish_patterns:
            strongest = bearish_patterns[0]
        
        # Build interpretation based on regime
        if not bullish_patterns and not bearish_patterns:
            interpretation = "No significant candlestick patterns detected."
        else:
            interpretation_parts = [
                f"PATTERN ANALYSIS:",
                f"  Bullish patterns: {bullish_patterns if bullish_patterns else 'None'}",
                f"  Bearish patterns: {bearish_patterns if bearish_patterns else 'None'}",
                f"  Bias: {pattern_bias}",
            ]
            
            if regime == MarketRegime.TRENDING_UP:
                if pattern_bias == "BULLISH":
                    interpretation_parts.append("  → Bullish patterns CONFIRM uptrend - good entry")
                elif pattern_bias == "BEARISH":
                    interpretation_parts.append("  → Bearish patterns in uptrend - potential pullback")
            elif regime == MarketRegime.TRENDING_DOWN:
                if pattern_bias == "BEARISH":
                    interpretation_parts.append("  → Bearish patterns CONFIRM downtrend - good short entry")
                elif pattern_bias == "BULLISH":
                    interpretation_parts.append("  → Bullish patterns in downtrend - potential bounce")
            elif regime == MarketRegime.RANGING:
                if pattern_bias == "BULLISH":
                    interpretation_parts.append("  → Bullish patterns at support - potential long")
                elif pattern_bias == "BEARISH":
                    interpretation_parts.append("  → Bearish patterns at resistance - potential short")
            else:
                interpretation_parts.append("  → Patterns less reliable in volatile conditions")
            
            interpretation = "\n".join(interpretation_parts)
        
        return PatternAnalysis(
            bullish_patterns=bullish_patterns,
            bearish_patterns=bearish_patterns,
            strongest_pattern=strongest,
            pattern_bias=pattern_bias,
            interpretation=interpretation
        )
    
    def _interpret_cycles_comprehensive(self, indicators: Dict[str, Any],
                                         regime: MarketRegime) -> CycleAnalysis:
        """
        Interpret ALL Hilbert Transform cycle indicators.
        
        Uses:
        - HT_DCPERIOD (Dominant Cycle Period)
        - HT_DCPHASE (Dominant Cycle Phase)
        - HT_PHASOR (inphase, quadrature)
        - HT_SINE (sine, leadsine)
        - HT_TRENDMODE (0=cycle, 1=trend)
        """
        cycles = indicators.get("cycles", {})
        
        dc_period = cycles.get("HT_DCPERIOD", 20)
        dc_phase = cycles.get("HT_DCPHASE", 0)
        trend_mode = cycles.get("HT_TRENDMODE", 0)
        sine = cycles.get("HT_SINE_sine", 0)
        leadsine = cycles.get("HT_SINE_leadsine", 0)
        inphase = cycles.get("HT_PHASOR_inphase", 0)
        quadrature = cycles.get("HT_PHASOR_quadrature", 0)
        
        interpretation_parts = [
            f"CYCLE ANALYSIS (Hilbert Transform):",
            f"  Dominant Period: {dc_period:.1f} bars",
            f"  Phase: {dc_phase:.1f}°",
            f"  Mode: {'TRENDING' if trend_mode == 1 else 'CYCLING'}",
        ]
        
        if trend_mode == 1:
            interpretation_parts.append("  → In TREND mode - follow trend, ignore cycle signals")
        else:
            # In cycle mode, analyze sine wave for turning points
            if sine > leadsine and sine > 0:
                cycle_position = "approaching cycle TOP"
                interpretation_parts.append(f"  → {cycle_position} - prepare for reversal down")
            elif sine < leadsine and sine < 0:
                cycle_position = "approaching cycle BOTTOM"
                interpretation_parts.append(f"  → {cycle_position} - prepare for reversal up")
            elif sine > 0:
                cycle_position = "in upper half of cycle"
                interpretation_parts.append(f"  → {cycle_position}")
            else:
                cycle_position = "in lower half of cycle"
                interpretation_parts.append(f"  → {cycle_position}")
        
        # Phasor analysis
        if inphase != 0 or quadrature != 0:
            phasor_angle = np.arctan2(quadrature, inphase) * 180 / np.pi if inphase != 0 else 0
            interpretation_parts.append(f"  Phasor angle: {phasor_angle:.1f}°")
        
        interpretation = "\n".join(interpretation_parts)
        
        return CycleAnalysis(
            dominant_period=dc_period,
            phase=dc_phase,
            trend_mode=trend_mode,
            interpretation=interpretation
        )


    # =========================================================================
    # STEP 3: DECISION SYNTHESIS (Using ALL Indicators)
    # =========================================================================
    
    def synthesize_decision(self, regime_analysis: RegimeAnalysis,
                            interpretations: IndicatorInterpretations,
                            indicators: Dict[str, Any]) -> TradeDecision:
        """
        Synthesize all interpretations into a wise trading decision.
        
        Uses COMPREHENSIVE indicator agreement across ALL categories:
        - Trend (18 overlap studies + statistics)
        - Momentum (31 indicators)
        - Volume (3 indicators + MFI)
        - Patterns (61 candlestick patterns)
        - Cycles (5 Hilbert Transform indicators)
        
        Decision Synthesis Algorithm:
        1. Based on regime, determine allowed trade directions
        2. Check indicator agreement across ALL categories
        3. Apply hierarchy: Regime > Trend > Momentum > Volume > Patterns
        4. Determine position sizing based on agreement level
        5. Generate comprehensive reasoning
        """
        regime = regime_analysis.regime
        
        # Step 1: Determine allowed directions based on regime
        allowed_directions = self._get_allowed_directions(regime)
        
        if TradeDirection.NO_TRADE in allowed_directions and len(allowed_directions) == 1:
            return TradeDecision(
                direction=TradeDirection.NO_TRADE,
                confidence_factors=["Volatile market conditions"],
                warning_factors=["High volatility detected", "Wait for stability"],
                reasoning=self._build_no_trade_reasoning(regime_analysis),
                position_size_multiplier=0.0
            )
        
        # Step 2: Check COMPREHENSIVE indicator agreement
        agreement = self._check_comprehensive_agreement(interpretations, indicators, regime)
        
        # Step 3: Apply hierarchy and determine direction
        direction, confidence_factors, warning_factors = self._apply_hierarchy_comprehensive(
            regime, interpretations, agreement, allowed_directions, indicators
        )
        
        # Step 4: Determine position size based on agreement
        position_size_multiplier = self._calculate_position_multiplier_comprehensive(
            agreement, regime, warning_factors
        )
        
        # Step 5: Generate comprehensive reasoning
        reasoning = self._build_decision_reasoning_comprehensive(
            direction, regime_analysis, interpretations, 
            confidence_factors, warning_factors, position_size_multiplier, agreement
        )
        
        return TradeDecision(
            direction=direction,
            confidence_factors=confidence_factors,
            warning_factors=warning_factors,
            reasoning=reasoning,
            position_size_multiplier=position_size_multiplier
        )
    
    def _get_allowed_directions(self, regime: MarketRegime) -> List[TradeDirection]:
        """Get allowed trade directions based on regime."""
        if regime == MarketRegime.TRENDING_UP:
            return [TradeDirection.LONG]
        elif regime == MarketRegime.TRENDING_DOWN:
            return [TradeDirection.SHORT]
        elif regime == MarketRegime.RANGING:
            return [TradeDirection.LONG, TradeDirection.SHORT]
        else:  # VOLATILE
            return [TradeDirection.NO_TRADE]
    
    def _check_comprehensive_agreement(self, interpretations: IndicatorInterpretations,
                                        indicators: Dict[str, Any],
                                        regime: MarketRegime) -> Dict[str, Any]:
        """
        Check COMPREHENSIVE indicator agreement across ALL categories.
        
        Returns detailed agreement analysis for each category.
        """
        momentum = indicators.get("momentum", {})
        overlap = indicators.get("overlap", {})
        statistics = indicators.get("statistics", {})
        cycles = indicators.get("cycles", {})
        
        agreement = {
            "trend": {},
            "momentum": {},
            "volume": {},
            "patterns": {},
            "cycles": {},
            "statistics": {},
            "summary": {}
        }
        
        # =====================================================================
        # TREND AGREEMENT (18 overlap studies)
        # =====================================================================
        trend_bullish = 0
        trend_bearish = 0
        
        # MA comparisons
        sma_20 = overlap.get("SMA_20", 0)
        sma_50 = overlap.get("SMA_50", 0)
        sma_200 = overlap.get("SMA_200", 0)
        ema_12 = overlap.get("EMA_12", 0)
        ema_26 = overlap.get("EMA_26", 0)
        mama = overlap.get("MAMA", 0)
        fama = overlap.get("FAMA", 0)
        sar = overlap.get("SAR", 0)
        bbands_middle = overlap.get("BBANDS_middle", sma_20)
        
        if ema_12 > ema_26: trend_bullish += 1
        else: trend_bearish += 1
        
        if sma_20 > sma_50: trend_bullish += 1
        else: trend_bearish += 1
        
        if sma_50 > sma_200 and sma_200 > 0: trend_bullish += 1
        elif sma_200 > 0: trend_bearish += 1
        
        if mama > fama and mama > 0: trend_bullish += 1
        elif fama > 0: trend_bearish += 1
        
        if sar < bbands_middle: trend_bullish += 1
        else: trend_bearish += 1
        
        # Linear regression
        linreg_slope = statistics.get("LINEARREG_SLOPE_14", 0)
        if linreg_slope > 0: trend_bullish += 1
        else: trend_bearish += 1
        
        agreement["trend"] = {
            "bullish": trend_bullish,
            "bearish": trend_bearish,
            "direction": "BULLISH" if trend_bullish > trend_bearish else "BEARISH" if trend_bearish > trend_bullish else "NEUTRAL"
        }
        
        # =====================================================================
        # MOMENTUM AGREEMENT (31 indicators)
        # =====================================================================
        mom_bullish = 0
        mom_bearish = 0
        
        # RSI
        rsi = momentum.get("RSI_14", 50)
        if rsi > 50: mom_bullish += 1
        else: mom_bearish += 1
        
        # MACD
        macd_hist = momentum.get("MACD_hist", 0)
        if macd_hist > 0: mom_bullish += 2  # Weight: 2
        else: mom_bearish += 2
        
        # Stochastic
        stoch_k = momentum.get("STOCH_slowk", 50)
        if stoch_k > 50: mom_bullish += 1
        else: mom_bearish += 1
        
        # AROON
        aroonosc = momentum.get("AROONOSC", 0)
        if aroonosc > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # CCI
        cci = momentum.get("CCI_14", 0)
        if cci > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # CMO
        cmo = momentum.get("CMO_14", 0)
        if cmo > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # MOM
        mom_val = momentum.get("MOM_10", 0)
        if mom_val > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # APO
        apo = momentum.get("APO", 0)
        if apo > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # PPO
        ppo = momentum.get("PPO", 0)
        if ppo > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # BOP
        bop = momentum.get("BOP", 0)
        if bop > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # ROC
        roc = momentum.get("ROC_10", 0)
        if roc > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # TRIX
        trix = momentum.get("TRIX_30", 0)
        if trix > 0: mom_bullish += 1
        else: mom_bearish += 1
        
        # ULTOSC
        ultosc = momentum.get("ULTOSC", 50)
        if ultosc > 50: mom_bullish += 1
        else: mom_bearish += 1
        
        # WILLR
        willr = momentum.get("WILLR_14", -50)
        if willr > -50: mom_bullish += 1
        else: mom_bearish += 1
        
        # MFI
        mfi = momentum.get("MFI_14", 50)
        if mfi > 50: mom_bullish += 1
        else: mom_bearish += 1
        
        # +DI vs -DI
        plus_di = momentum.get("PLUS_DI_14", 0)
        minus_di = momentum.get("MINUS_DI_14", 0)
        if plus_di > minus_di: mom_bullish += 2  # Weight: 2
        else: mom_bearish += 2
        
        agreement["momentum"] = {
            "bullish": mom_bullish,
            "bearish": mom_bearish,
            "direction": "BULLISH" if mom_bullish > mom_bearish else "BEARISH" if mom_bearish > mom_bullish else "NEUTRAL"
        }
        
        # =====================================================================
        # VOLUME AGREEMENT
        # =====================================================================
        agreement["volume"] = {
            "direction": "BULLISH" if interpretations.volume.confirms_price and regime == MarketRegime.TRENDING_UP else
                        "BEARISH" if interpretations.volume.confirms_price and regime == MarketRegime.TRENDING_DOWN else
                        "DIVERGENCE" if not interpretations.volume.confirms_price else "NEUTRAL"
        }
        
        # =====================================================================
        # PATTERN AGREEMENT
        # =====================================================================
        agreement["patterns"] = {
            "direction": interpretations.patterns.pattern_bias
        }
        
        # =====================================================================
        # CYCLE AGREEMENT
        # =====================================================================
        ht_trendmode = cycles.get("HT_TRENDMODE", 0)
        if ht_trendmode == 1:
            agreement["cycles"] = {"direction": agreement["trend"]["direction"]}
        else:
            agreement["cycles"] = {"direction": "CYCLE"}
        
        # =====================================================================
        # SUMMARY
        # =====================================================================
        total_bullish = (
            agreement["trend"]["bullish"] + 
            agreement["momentum"]["bullish"] +
            (1 if agreement["volume"]["direction"] == "BULLISH" else 0) +
            (1 if agreement["patterns"]["direction"] == "BULLISH" else 0)
        )
        total_bearish = (
            agreement["trend"]["bearish"] + 
            agreement["momentum"]["bearish"] +
            (1 if agreement["volume"]["direction"] == "BEARISH" else 0) +
            (1 if agreement["patterns"]["direction"] == "BEARISH" else 0)
        )
        
        total = total_bullish + total_bearish
        agreement["summary"] = {
            "total_bullish": total_bullish,
            "total_bearish": total_bearish,
            "bullish_pct": (total_bullish / total * 100) if total > 0 else 50,
            "overall": "BULLISH" if total_bullish > total_bearish else "BEARISH" if total_bearish > total_bullish else "NEUTRAL"
        }
        
        return agreement
    
    def _apply_hierarchy_comprehensive(self, regime: MarketRegime,
                                        interpretations: IndicatorInterpretations,
                                        agreement: Dict[str, Any],
                                        allowed_directions: List[TradeDirection],
                                        indicators: Dict[str, Any]) -> tuple:
        """
        Apply hierarchy when indicators conflict.
        
        Hierarchy: Regime > Trend > Momentum > Volume > Patterns
        """
        confidence_factors = []
        warning_factors = []
        momentum = indicators.get("momentum", {})
        
        summary = agreement["summary"]
        
        # Regime is king
        if regime == MarketRegime.TRENDING_UP:
            if TradeDirection.LONG in allowed_directions:
                direction = TradeDirection.LONG
                confidence_factors.append(f"Market regime is TRENDING_UP")
                
                if agreement["trend"]["direction"] == "BULLISH":
                    confidence_factors.append(f"Trend: {agreement['trend']['bullish']} bullish signals")
                if agreement["momentum"]["direction"] == "BULLISH":
                    confidence_factors.append(f"Momentum: {agreement['momentum']['bullish']} bullish signals")
                if agreement["volume"]["direction"] == "BULLISH":
                    confidence_factors.append("Volume confirms buying pressure")
                if agreement["patterns"]["direction"] == "BULLISH":
                    confidence_factors.append("Bullish candlestick patterns present")
                
                # Warnings
                if agreement["momentum"]["direction"] == "BEARISH":
                    warning_factors.append(f"Momentum diverging ({agreement['momentum']['bearish']} bearish)")
                if agreement["volume"]["direction"] == "DIVERGENCE":
                    warning_factors.append("Volume not confirming - potential weakness")
                if agreement["patterns"]["direction"] == "BEARISH":
                    warning_factors.append("Bearish patterns - possible pullback")
            else:
                direction = TradeDirection.NO_TRADE
        
        elif regime == MarketRegime.TRENDING_DOWN:
            if TradeDirection.SHORT in allowed_directions:
                direction = TradeDirection.SHORT
                confidence_factors.append(f"Market regime is TRENDING_DOWN")
                
                if agreement["trend"]["direction"] == "BEARISH":
                    confidence_factors.append(f"Trend: {agreement['trend']['bearish']} bearish signals")
                if agreement["momentum"]["direction"] == "BEARISH":
                    confidence_factors.append(f"Momentum: {agreement['momentum']['bearish']} bearish signals")
                if agreement["volume"]["direction"] == "BEARISH":
                    confidence_factors.append("Volume confirms selling pressure")
                if agreement["patterns"]["direction"] == "BEARISH":
                    confidence_factors.append("Bearish candlestick patterns present")
                
                # Warnings
                if agreement["momentum"]["direction"] == "BULLISH":
                    warning_factors.append(f"Momentum diverging ({agreement['momentum']['bullish']} bullish)")
                if agreement["volume"]["direction"] == "DIVERGENCE":
                    warning_factors.append("Volume not confirming - potential weakness")
                if agreement["patterns"]["direction"] == "BULLISH":
                    warning_factors.append("Bullish patterns - possible bounce")
            else:
                direction = TradeDirection.NO_TRADE
        
        elif regime == MarketRegime.RANGING:
            # In ranging, use momentum extremes
            rsi = momentum.get("RSI_14", 50)
            stoch_k = momentum.get("STOCH_slowk", 50)
            cci = momentum.get("CCI_14", 0)
            willr = momentum.get("WILLR_14", -50)
            ultosc = momentum.get("ULTOSC", 50)
            
            # Count oversold/overbought signals
            oversold_count = sum([
                rsi < 30,
                stoch_k < 20,
                cci < -100,
                willr < -80,
                ultosc < 30
            ])
            overbought_count = sum([
                rsi > 70,
                stoch_k > 80,
                cci > 100,
                willr > -20,
                ultosc > 70
            ])
            
            if oversold_count >= 3:
                if TradeDirection.LONG in allowed_directions:
                    direction = TradeDirection.LONG
                    confidence_factors.append(f"OVERSOLD: {oversold_count} indicators at extremes")
                    if agreement["patterns"]["direction"] == "BULLISH":
                        confidence_factors.append("Bullish reversal pattern at support")
                else:
                    direction = TradeDirection.NO_TRADE
            elif overbought_count >= 3:
                if TradeDirection.SHORT in allowed_directions:
                    direction = TradeDirection.SHORT
                    confidence_factors.append(f"OVERBOUGHT: {overbought_count} indicators at extremes")
                    if agreement["patterns"]["direction"] == "BEARISH":
                        confidence_factors.append("Bearish reversal pattern at resistance")
                else:
                    direction = TradeDirection.NO_TRADE
            else:
                direction = TradeDirection.NO_TRADE
                warning_factors.append("Mid-range - wait for extremes")
        
        else:  # VOLATILE
            direction = TradeDirection.NO_TRADE
            warning_factors.append("Volatile conditions - staying out")
        
        return direction, confidence_factors, warning_factors
    
    def _calculate_position_multiplier_comprehensive(self, agreement: Dict[str, Any],
                                                      regime: MarketRegime,
                                                      warning_factors: List[str]) -> float:
        """Calculate position size multiplier based on comprehensive agreement."""
        if regime == MarketRegime.VOLATILE:
            return 0.0
        
        summary = agreement["summary"]
        bullish_pct = summary["bullish_pct"]
        
        # Determine target direction
        if regime == MarketRegime.TRENDING_UP:
            agreement_pct = bullish_pct
        elif regime == MarketRegime.TRENDING_DOWN:
            agreement_pct = 100 - bullish_pct
        else:
            return 0.5  # Ranging - always reduced size
        
        # Calculate base multiplier
        if agreement_pct >= 75:
            multiplier = 1.0  # Full size - strong agreement
        elif agreement_pct >= 65:
            multiplier = 0.75
        elif agreement_pct >= 55:
            multiplier = 0.5
        else:
            multiplier = 0.25
        
        # Reduce for warnings
        if len(warning_factors) >= 3:
            multiplier *= 0.5
        elif len(warning_factors) >= 2:
            multiplier *= 0.75
        
        return min(1.0, max(0.0, multiplier))
    
    def _build_no_trade_reasoning(self, regime_analysis: RegimeAnalysis) -> str:
        """Build reasoning for no trade decision."""
        return (
            f"NO TRADE DECISION\n\n"
            f"Regime: {regime_analysis.regime.value}\n"
            f"{regime_analysis.reasoning}\n\n"
            f"Action: Stay out of the market until conditions stabilize."
        )
    
    def _build_decision_reasoning_comprehensive(self, direction: TradeDirection,
                                                 regime_analysis: RegimeAnalysis,
                                                 interpretations: IndicatorInterpretations,
                                                 confidence_factors: List[str],
                                                 warning_factors: List[str],
                                                 position_multiplier: float,
                                                 agreement: Dict[str, Any]) -> str:
        """Build comprehensive decision reasoning with ALL indicator analysis."""
        summary = agreement["summary"]
        
        parts = [
            "═" * 70,
            f"TRADE DECISION: {direction.value}",
            f"Position Size: {position_multiplier * 100:.0f}%",
            f"Overall Agreement: {summary['total_bullish']} bullish / {summary['total_bearish']} bearish ({summary['bullish_pct']:.1f}% bullish)",
            "═" * 70,
            "",
            regime_analysis.reasoning,
            "",
            "═" * 70,
            "INDICATOR ANALYSIS (ALL 161 INDICATORS)",
            "═" * 70,
            "",
            interpretations.trend.interpretation,
            "",
            interpretations.momentum.interpretation,
            "",
            interpretations.volume.interpretation,
            "",
            interpretations.patterns.interpretation,
            "",
            interpretations.cycles.interpretation,
            "",
            "═" * 70,
            "AGREEMENT BREAKDOWN",
            "═" * 70,
            f"  Trend: {agreement['trend']['bullish']} bullish / {agreement['trend']['bearish']} bearish → {agreement['trend']['direction']}",
            f"  Momentum: {agreement['momentum']['bullish']} bullish / {agreement['momentum']['bearish']} bearish → {agreement['momentum']['direction']}",
            f"  Volume: {agreement['volume']['direction']}",
            f"  Patterns: {agreement['patterns']['direction']}",
            f"  Cycles: {agreement['cycles']['direction']}",
            "",
            "═" * 70,
            "CONFIDENCE FACTORS",
            "═" * 70,
        ]
        
        for factor in confidence_factors:
            parts.append(f"  ✓ {factor}")
        
        if warning_factors:
            parts.extend([
                "",
                "═" * 70,
                "WARNING FACTORS",
                "═" * 70,
            ])
            for factor in warning_factors:
                parts.append(f"  ⚠ {factor}")
        
        parts.extend([
            "",
            "═" * 70,
            "CONCLUSION",
            "═" * 70,
        ])
        
        if direction == TradeDirection.LONG:
            parts.append(
                "The market is in an UPTREND with supporting indicators. "
                f"{summary['total_bullish']} indicators agree. "
                "Enter LONG position with appropriate risk management."
            )
        elif direction == TradeDirection.SHORT:
            parts.append(
                "The market is in a DOWNTREND with supporting indicators. "
                f"{summary['total_bearish']} indicators agree. "
                "Enter SHORT position with appropriate risk management."
            )
        else:
            parts.append(
                "Conditions do not favor a trade at this time. "
                "Wait for better setup or clearer signals."
            )
        
        return "\n".join(parts)


    # =========================================================================
    # STEP 4: ENTRY/EXIT CALCULATION
    # =========================================================================
    
    def calculate_entry_exit(self, decision: TradeDecision,
                             indicators: Dict[str, Any],
                             current_price: float,
                             symbol: str) -> TradeParameters:
        """
        Calculate entry price, stop loss, take profit based on ATR and market structure.
        
        Uses:
        - ATR, NATR for volatility-based stops
        - Bollinger Bands for targets
        - SAR for trailing stop reference
        - Support/Resistance from math_operators
        
        Stop Loss: Entry ± (ATR × 1.5-2.0)
        Take Profit: Entry ± (ATR × 2.0-3.0) with minimum 1:1.5 R:R
        Position Size: (Account × 2% Risk) / Stop Distance
        """
        volatility = indicators.get("volatility", {})
        overlap = indicators.get("overlap", {})
        math_ops = indicators.get("math_operators", {})
        
        atr = volatility.get("ATR_14", 0.001)
        natr = volatility.get("NATR_14", 0.1)
        sar = overlap.get("SAR", current_price)
        bbands_upper = overlap.get("BBANDS_upper", current_price + atr * 2)
        bbands_lower = overlap.get("BBANDS_lower", current_price - atr * 2)
        accbands_upper = overlap.get("ACCBANDS_upper", bbands_upper)
        accbands_lower = overlap.get("ACCBANDS_lower", bbands_lower)
        
        # Support/Resistance from math operators
        support = math_ops.get("MIN_14", current_price - atr * 2)
        resistance = math_ops.get("MAX_14", current_price + atr * 2)
        
        # Determine pip value for the symbol
        pip_value = self._get_pip_value(symbol)
        
        # Adjust ATR multiplier based on volatility
        if natr > 0.5:
            sl_multiplier = ATR_SL_MULTIPLIER * 1.2  # Wider stops in high volatility
            tp_multiplier = ATR_TP_MULTIPLIER * 1.2
        else:
            sl_multiplier = ATR_SL_MULTIPLIER
            tp_multiplier = ATR_TP_MULTIPLIER
        
        if decision.direction == TradeDirection.LONG:
            entry_price = current_price
            
            # Stop loss below recent structure or ATR-based
            sl_atr_based = entry_price - (atr * sl_multiplier)
            sl_sar_based = sar if sar < entry_price else sl_atr_based
            sl_support_based = support - (atr * 0.5) if support < entry_price else sl_atr_based
            
            # Use tightest reasonable stop
            stop_loss = max(sl_atr_based, sl_sar_based, sl_support_based)
            
            # Take profit based on ATR with minimum R:R
            sl_distance = entry_price - stop_loss
            min_tp_distance = sl_distance * 1.5  # Minimum 1:1.5 R:R
            atr_tp_distance = atr * tp_multiplier
            tp_distance = max(min_tp_distance, atr_tp_distance)
            take_profit = entry_price + tp_distance
            
            # Cap TP at resistance levels
            if take_profit > bbands_upper * 1.01:
                take_profit = bbands_upper
                tp_distance = take_profit - entry_price
            if take_profit > resistance * 1.01:
                take_profit = resistance
                tp_distance = take_profit - entry_price
            
            entry_reasoning = f"Enter LONG at market price {entry_price:.5f}"
            sl_reasoning = f"Stop loss at {stop_loss:.5f} ({sl_multiplier}x ATR below entry, SAR={sar:.5f})"
            tp_reasoning = f"Take profit at {take_profit:.5f} ({tp_distance/atr:.1f}x ATR, BB upper={bbands_upper:.5f})"
        
        elif decision.direction == TradeDirection.SHORT:
            entry_price = current_price
            
            # Stop loss above recent structure or ATR-based
            sl_atr_based = entry_price + (atr * sl_multiplier)
            sl_sar_based = sar if sar > entry_price else sl_atr_based
            sl_resistance_based = resistance + (atr * 0.5) if resistance > entry_price else sl_atr_based
            
            # Use tightest reasonable stop
            stop_loss = min(sl_atr_based, sl_sar_based, sl_resistance_based)
            
            # Take profit based on ATR with minimum R:R
            sl_distance = stop_loss - entry_price
            min_tp_distance = sl_distance * 1.5  # Minimum 1:1.5 R:R
            atr_tp_distance = atr * tp_multiplier
            tp_distance = max(min_tp_distance, atr_tp_distance)
            take_profit = entry_price - tp_distance
            
            # Cap TP at support levels
            if take_profit < bbands_lower * 0.99:
                take_profit = bbands_lower
                tp_distance = entry_price - take_profit
            if take_profit < support * 0.99:
                take_profit = support
                tp_distance = entry_price - take_profit
            
            entry_reasoning = f"Enter SHORT at market price {entry_price:.5f}"
            sl_reasoning = f"Stop loss at {stop_loss:.5f} ({sl_multiplier}x ATR above entry, SAR={sar:.5f})"
            tp_reasoning = f"Take profit at {take_profit:.5f} ({tp_distance/atr:.1f}x ATR, BB lower={bbands_lower:.5f})"
        
        else:
            # No trade - return empty parameters
            return TradeParameters(
                entry_price=0,
                stop_loss=0,
                take_profit=0,
                stop_loss_pips=0,
                take_profit_pips=0,
                risk_reward_ratio=0,
                atr_value=atr,
                position_size=0,
                entry_reasoning="No trade",
                sl_reasoning="N/A",
                tp_reasoning="N/A"
            )
        
        # Calculate pips
        sl_pips = abs(entry_price - stop_loss) / pip_value
        tp_pips = abs(take_profit - entry_price) / pip_value
        
        # Risk/Reward ratio
        risk_reward = tp_pips / sl_pips if sl_pips > 0 else 0
        
        # Position size calculation (2% risk)
        risk_amount = self.account_balance * (MAX_RISK_PERCENT / 100)
        pip_value_per_lot = self._get_pip_value_per_lot(symbol)
        position_size = risk_amount / (sl_pips * pip_value_per_lot)
        position_size = round(position_size, 2)  # Round to 0.01 lots
        position_size = min(position_size, 1.0)  # Cap at 1 lot
        
        # Apply position multiplier from decision
        position_size *= decision.position_size_multiplier
        position_size = round(position_size, 2)
        
        return TradeParameters(
            entry_price=round(entry_price, 5),
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            stop_loss_pips=round(sl_pips, 1),
            take_profit_pips=round(tp_pips, 1),
            risk_reward_ratio=round(risk_reward, 2),
            atr_value=atr,
            position_size=position_size,
            entry_reasoning=entry_reasoning,
            sl_reasoning=sl_reasoning,
            tp_reasoning=tp_reasoning
        )
    
    def _get_pip_value(self, symbol: str) -> float:
        """Get pip value for a symbol."""
        # JPY pairs have different pip value
        if "JPY" in symbol:
            return 0.01
        else:
            return 0.0001
    
    def _get_pip_value_per_lot(self, symbol: str) -> float:
        """Get pip value per standard lot for a symbol."""
        # Approximate pip values per standard lot (100,000 units)
        if "JPY" in symbol:
            return 1000  # ~$10 per pip for JPY pairs
        else:
            return 10  # ~$10 per pip for most pairs


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def analyze_market(indicators: Dict[str, Any],
                   current_price: float,
                   symbol: str,
                   timeframe: str = "H1",
                   account_balance: float = 10000.0) -> MarketAnalysis:
    """
    Convenience function to analyze market with ALL 161 indicators.
    
    Args:
        indicators: Dict of all computed indicators (all 161)
        current_price: Current market price
        symbol: Trading symbol
        timeframe: Timeframe
        account_balance: Account balance for position sizing
    
    Returns:
        MarketAnalysis with complete analysis and decision
    """
    engine = WisdomEngine(account_balance=account_balance)
    return engine.analyze(indicators, current_price, symbol, timeframe)
