# KUIPER V2 - COMPLETE INDICATOR KNOWLEDGE BASE
## Understanding ALL 161 TA-Lib Indicators for Wise Trading Decisions

================================================================================

# TABLE OF CONTENTS

1. [Introduction & Philosophy](#1-introduction--philosophy)
2. [Market Regime Framework](#2-market-regime-framework)
3. [Overlap Studies (18 Indicators)](#3-overlap-studies-18-indicators)
4. [Momentum Indicators (31 Indicators)](#4-momentum-indicators-31-indicators)
5. [Volume Indicators (3 Indicators)](#5-volume-indicators-3-indicators)
6. [Volatility Indicators (3 Indicators)](#6-volatility-indicators-3-indicators)
7. [Cycle Indicators (5 Indicators)](#7-cycle-indicators-5-indicators)
8. [Price Transform (5 Indicators)](#8-price-transform-5-indicators)
9. [Statistical Functions (9 Indicators)](#9-statistical-functions-9-indicators)
10. [Pattern Recognition (61 Indicators)](#10-pattern-recognition-61-indicators)
11. [Math Transform (15 Functions)](#11-math-transform-15-functions)
12. [Math Operators (11 Functions)](#12-math-operators-11-functions)
13. [Indicator Hierarchy & Conflict Resolution](#13-indicator-hierarchy--conflict-resolution)
14. [Context-Aware Interpretation Rules](#14-context-aware-interpretation-rules)

================================================================================

# 1. INTRODUCTION & PHILOSOPHY

## Purpose of This Document

This knowledge base provides the Wisdom Engine with DEEP UNDERSTANDING of what 
each indicator MEANS and HOW to interpret it in different market contexts.

**This is NOT a confidence-based scoring system.**

The Wisdom Engine must:
1. UNDERSTAND what each indicator is telling us about the market
2. INTERPRET indicators IN CONTEXT of the current market regime
3. SYNTHESIZE all information into a WISE trading decision
4. PROVIDE FULL REASONING for every decision

## The Hierarchy of Analysis

When indicators conflict, follow this priority:

```
1. REGIME (Trending Up, Trending Down, Ranging, Volatile)
   ↓
2. TREND (Direction and Strength from MAs, ADX, AROON)
   ↓
3. MOMENTUM (RSI, MACD, Stochastic, CCI, etc.)
   ↓
4. VOLUME (AD, ADOSC, OBV - confirms or denies)
   ↓
5. PATTERNS (Candlestick patterns - timing refinement)
```

## Key Principle: Context Changes Everything

The SAME indicator value means DIFFERENT things in different regimes:

| Indicator | Trending Up | Trending Down | Ranging | Volatile |
|-----------|-------------|---------------|---------|----------|
| RSI = 30 | Pullback opportunity | Trend continuation | Oversold, buy | Unreliable |
| RSI = 70 | Trend strength | Bounce to short | Overbought, sell | Unreliable |
| Price at Upper BB | Walking the band | Resistance | Overbought | Expansion |
| Price at Lower BB | Support | Walking the band | Oversold | Expansion |

================================================================================

# 2. MARKET REGIME FRAMEWORK

## The Four Market Regimes

### 1. TRENDING UP
**Characteristics:**
- ADX > 25 with +DI > -DI
- Price above rising MAs (SMA20 > SMA50 > SMA200)
- Higher highs and higher lows
- HT_TRENDMODE = 1 (trending)
- AROON Up > 70, AROON Down < 30

**Trading Approach:**
- ONLY look for LONG opportunities
- Buy pullbacks to MAs or lower Bollinger Band
- RSI oversold = buying opportunity, NOT reversal
- Don't short overbought conditions

### 2. TRENDING DOWN
**Characteristics:**
- ADX > 25 with -DI > +DI
- Price below falling MAs (SMA20 < SMA50 < SMA200)
- Lower highs and lower lows
- HT_TRENDMODE = 1 (trending)
- AROON Down > 70, AROON Up < 30

**Trading Approach:**
- ONLY look for SHORT opportunities
- Sell rallies to MAs or upper Bollinger Band
- RSI overbought = shorting opportunity, NOT reversal
- Don't buy oversold conditions

### 3. RANGING (Sideways)
**Characteristics:**
- ADX < 20 (no trend)
- Price oscillating between support and resistance
- MAs are flat and intertwined
- HT_TRENDMODE = 0 (cycling)
- AROON oscillating, no clear dominance

**Trading Approach:**
- Mean reversion strategies work
- Buy at support/lower BB, sell at resistance/upper BB
- RSI overbought/oversold ARE reversal signals
- Use oscillators (RSI, Stochastic, CCI)

### 4. VOLATILE
**Characteristics:**
- NATR > 1.0% (extreme volatility)
- ATR spiking above normal
- Wide Bollinger Bands
- Erratic price movements
- News-driven or panic conditions

**Trading Approach:**
- REDUCE position size or stay out
- Indicators are UNRELIABLE
- Wait for volatility to normalize
- If trading, use wider stops

================================================================================

# 3. OVERLAP STUDIES (18 INDICATORS)

## Overview
Overlap studies are plotted directly on the price chart. They help identify 
trend direction, support/resistance levels, and potential entry/exit points.

---

## 3.1 SMA - Simple Moving Average

**What It Is:**
The arithmetic mean of prices over a specified period.

**Formula:**
```
SMA = (P1 + P2 + ... + Pn) / n
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| Price > SMA | Bullish bias |
| Price < SMA | Bearish bias |
| SMA rising | Uptrend |
| SMA falling | Downtrend |
| SMA flat | No trend |

**Key Periods:**
- SMA(20): Short-term trend
- SMA(50): Medium-term trend
- SMA(200): Long-term trend (institutional)

**Golden Cross:** SMA(50) crosses above SMA(200) → Bullish
**Death Cross:** SMA(50) crosses below SMA(200) → Bearish

**Context-Aware Usage:**
- In UPTREND: SMA acts as dynamic support
- In DOWNTREND: SMA acts as dynamic resistance
- In RANGING: Price oscillates around SMA

---

## 3.2 EMA - Exponential Moving Average

**What It Is:**
A weighted moving average that gives more weight to recent prices.

**Formula:**
```
EMA = Price × k + EMA(prev) × (1 - k)
Where k = 2 / (period + 1)
```

**Why Use EMA Over SMA:**
- Reacts faster to price changes
- Better for short-term trading
- Less lag than SMA

**Key Periods:**
- EMA(12) and EMA(26): Used in MACD
- EMA(9): Fast signal line
- EMA(50): Medium-term trend

**Interpretation:**
- EMA(12) > EMA(26): Bullish momentum
- EMA(12) < EMA(26): Bearish momentum
- Price bouncing off EMA: Trend continuation

---

## 3.3 DEMA - Double Exponential Moving Average

**What It Is:**
Reduces lag by applying EMA twice with a correction factor.

**Formula:**
```
DEMA = 2 × EMA(n) - EMA(EMA(n))
```

**Interpretation:**
- Faster than EMA, less lag
- Better for catching trend changes early
- More prone to whipsaws in ranging markets

**Best Use:**
- Fast-moving markets
- When you need early signals
- Combine with slower MA for confirmation

---

## 3.4 TEMA - Triple Exponential Moving Average

**What It Is:**
Further reduces lag by applying EMA three times.

**Formula:**
```
TEMA = 3×EMA - 3×EMA(EMA) + EMA(EMA(EMA))
```

**Interpretation:**
- Fastest of the EMA variants
- Minimal lag
- Best for very short-term trading

**Caution:**
- Very sensitive to price changes
- Can generate many false signals
- Use in trending markets only

---

## 3.5 T3 - Triple Exponential Moving Average (Tillson)

**What It Is:**
Tim Tillson's smoothed version of TEMA with a volume factor.

**Interpretation:**
- Smoother than TEMA
- Less whipsaws
- Good balance of speed and smoothness

**Best Use:**
- When you want fast response without noise
- Swing trading
- Trend following

---

## 3.6 WMA - Weighted Moving Average

**What It Is:**
Assigns linearly increasing weights to recent prices.

**Formula:**
```
WMA = (P1×1 + P2×2 + ... + Pn×n) / (1+2+...+n)
```

**Interpretation:**
- More responsive than SMA
- Less responsive than EMA
- Good middle ground

---

## 3.7 TRIMA - Triangular Moving Average

**What It Is:**
Double-smoothed SMA that emphasizes middle of the period.

**Interpretation:**
- Very smooth, minimal noise
- Significant lag
- Best for identifying major trends

**Best Use:**
- Long-term trend identification
- Filtering out noise
- Not for timing entries

---

## 3.8 KAMA - Kaufman Adaptive Moving Average

**What It Is:**
Adapts its speed based on market volatility and direction.

**Key Innovation:**
- Fast in trending markets
- Slow in ranging markets
- Automatically adjusts

**Interpretation:**
| Market Condition | KAMA Behavior |
|------------------|---------------|
| Strong trend | Follows price closely |
| Choppy/ranging | Stays flat, filters noise |
| Breakout | Accelerates to catch move |

**Best Use:**
- All market conditions
- Reduces whipsaws in ranging markets
- Catches trends when they develop

---

## 3.9 MAMA/FAMA - MESA Adaptive Moving Average

**What It Is:**
John Ehlers' adaptive MA based on Hilbert Transform cycle analysis.

**Components:**
- MAMA: Mother of Adaptive Moving Averages (fast)
- FAMA: Following Adaptive Moving Average (slow)

**Interpretation:**
| Condition | Signal |
|-----------|--------|
| MAMA > FAMA | Bullish |
| MAMA < FAMA | Bearish |
| MAMA crosses above FAMA | Buy signal |
| MAMA crosses below FAMA | Sell signal |

**Best Use:**
- Cycle-based trading
- Adaptive trend following
- Works well in all market conditions

---

## 3.10 MAVP - Moving Average Variable Period

**What It Is:**
MA where the period changes based on another indicator.

**Best Use:**
- Advanced adaptive strategies
- When you want period to vary with volatility
- Custom indicator development

---

## 3.11 HT_TRENDLINE - Hilbert Transform Instantaneous Trendline

**What It Is:**
Cycle-based trendline using Hilbert Transform.

**Interpretation:**
- Represents the "true" trend without lag
- Price above HT_TRENDLINE: Bullish
- Price below HT_TRENDLINE: Bearish

**Best Use:**
- Identifying trend direction
- Cycle analysis
- Combine with HT_TRENDMODE

---

## 3.12 BBANDS - Bollinger Bands

**What It Is:**
Volatility bands placed above and below a moving average.

**Formula:**
```
Middle Band = SMA(20)
Upper Band = SMA(20) + 2 × StdDev(20)
Lower Band = SMA(20) - 2 × StdDev(20)
```

**Interpretation by Regime:**

| Regime | Upper Band | Lower Band | Middle Band |
|--------|------------|------------|-------------|
| Trending Up | Walking the band (bullish) | Support, buy dips | Dynamic support |
| Trending Down | Resistance, sell rallies | Walking the band (bearish) | Dynamic resistance |
| Ranging | Overbought, sell | Oversold, buy | Mean reversion target |
| Volatile | Expansion, caution | Expansion, caution | Unreliable |

**Key Concepts:**
- **Squeeze:** Bands narrow → Breakout imminent
- **Walking the Band:** Price stays at band → Strong trend
- **%B:** Position within bands (0 = lower, 1 = upper)
- **BandWidth:** Volatility measure

---

## 3.13 ACCBANDS - Acceleration Bands

**What It Is:**
Bands based on high-low range, not standard deviation.

**Formula:**
```
Upper = SMA(High × (1 + 4 × (High-Low)/((High+Low)/2)))
Lower = SMA(Low × (1 - 4 × (High-Low)/((High+Low)/2)))
```

**Interpretation:**
- Breakout above upper band: Strong bullish momentum
- Breakout below lower band: Strong bearish momentum
- Price inside bands: Normal trading

**Best Use:**
- Breakout confirmation
- Trend strength measurement
- Combine with Bollinger Bands

---

## 3.14 MIDPOINT

**What It Is:**
Midpoint of highest high and lowest low over period.

**Formula:**
```
MIDPOINT = (Highest High + Lowest Low) / 2
```

**Interpretation:**
- Price above MIDPOINT: Bullish bias
- Price below MIDPOINT: Bearish bias
- Acts as equilibrium level

---

## 3.15 MIDPRICE

**What It Is:**
Midpoint of high and low prices (current bar).

**Formula:**
```
MIDPRICE = (High + Low) / 2
```

**Best Use:**
- Intrabar analysis
- Fair value estimation
- Combine with other indicators

---

## 3.16 SAR - Parabolic SAR

**What It Is:**
Stop And Reverse indicator that trails price.

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| SAR below price | Uptrend, SAR is stop level |
| SAR above price | Downtrend, SAR is stop level |
| SAR flips | Trend reversal signal |

**Best Use:**
- Trailing stop placement
- Trend direction confirmation
- Exit signal generation

**Caution:**
- Whipsaws in ranging markets
- Use with trend filter (ADX > 25)

---

## 3.17 SAREXT - Parabolic SAR Extended

**What It Is:**
SAR with customizable acceleration factors.

**Parameters:**
- Start AF: Initial acceleration factor
- AF Increment: How much AF increases
- Max AF: Maximum acceleration factor

**Best Use:**
- Fine-tuning SAR for specific markets
- Adjusting sensitivity
- Custom trailing stop strategies

---

## 3.18 MA - Generic Moving Average

**What It Is:**
Wrapper function that can calculate any MA type.

**MA Types:**
- 0: SMA
- 1: EMA
- 2: WMA
- 3: DEMA
- 4: TEMA
- 5: TRIMA
- 6: KAMA
- 7: MAMA
- 8: T3

**Best Use:**
- Flexible MA calculation
- Strategy optimization
- Comparing MA types



================================================================================

# 4. MOMENTUM INDICATORS (31 INDICATORS)

## Overview
Momentum indicators measure the SPEED and STRENGTH of price movements.
They help identify overbought/oversold conditions, divergences, and trend strength.

---

## 4.1 RSI - Relative Strength Index

**Creator:** J. Welles Wilder Jr. (1978)

**What It Is:**
Measures the speed and magnitude of recent price changes on a 0-100 scale.

**Formula:**
```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss (over 14 periods)
```

**Standard Interpretation:**
| RSI Value | Condition |
|-----------|-----------|
| > 70 | Overbought |
| 50-70 | Bullish momentum |
| 30-50 | Bearish momentum |
| < 30 | Oversold |

**CRITICAL: Context-Aware Interpretation:**

| Regime | RSI > 70 | RSI < 30 |
|--------|----------|----------|
| TRENDING UP | Trend strength, NOT sell | Pullback opportunity, BUY |
| TRENDING DOWN | Bounce to short | Trend strength, NOT buy |
| RANGING | Overbought, SELL | Oversold, BUY |
| VOLATILE | Unreliable | Unreliable |

**Key Signals:**
- **Divergence:** Price makes new high/low but RSI doesn't → Reversal warning
- **Failure Swing:** RSI fails to make new extreme → Reversal confirmation
- **Centerline Cross:** RSI crossing 50 → Momentum shift

---

## 4.2 MACD - Moving Average Convergence Divergence

**Creator:** Gerald Appel (1979)

**What It Is:**
Shows relationship between two EMAs, revealing momentum changes.

**Components:**
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| MACD > 0 | Bullish (fast EMA above slow) |
| MACD < 0 | Bearish (fast EMA below slow) |
| MACD > Signal | Bullish momentum |
| MACD < Signal | Bearish momentum |
| Histogram growing | Momentum increasing |
| Histogram shrinking | Momentum decreasing |

**Key Signals:**
- **Signal Line Cross:** MACD crosses Signal → Trade signal
- **Zero Line Cross:** MACD crosses 0 → Trend confirmation
- **Divergence:** Price vs MACD divergence → Reversal warning

**Context-Aware Usage:**
- In UPTREND: Buy when MACD crosses above Signal below zero
- In DOWNTREND: Sell when MACD crosses below Signal above zero
- In RANGING: Trade both directions at extremes

---

## 4.3 MACDEXT - MACD Extended

**What It Is:**
MACD with customizable MA types for each component.

**Best Use:**
- Fine-tuning MACD for specific markets
- Using different MA types (EMA, SMA, DEMA, etc.)
- Strategy optimization

---

## 4.4 MACDFIX - MACD Fix

**What It Is:**
MACD with fixed 9-period signal line.

**Best Use:**
- When you want consistent signal line
- Comparing across different fast/slow periods

---

## 4.5 ADX - Average Directional Index

**Creator:** J. Welles Wilder Jr. (1978)

**What It Is:**
Measures TREND STRENGTH, not direction. Scale 0-100.

**Interpretation:**
| ADX Value | Trend Strength | Action |
|-----------|----------------|--------|
| 0-20 | Weak/No trend | Use ranging strategies |
| 20-25 | Emerging trend | Prepare for trend |
| 25-50 | Strong trend | Use trend-following |
| 50-75 | Very strong | Caution, may exhaust |
| 75-100 | Extreme | Expect reversal |

**Key Insight:**
- ADX tells you WHETHER to use trend or ranging strategies
- Rising ADX = Trend strengthening
- Falling ADX = Trend weakening

---

## 4.6 ADXR - Average Directional Movement Index Rating

**What It Is:**
Smoothed version of ADX (average of current and past ADX).

**Formula:**
```
ADXR = (ADX + ADX[n periods ago]) / 2
```

**Interpretation:**
- Smoother than ADX
- Confirms ADX readings
- Less prone to whipsaws

---

## 4.7 DX - Directional Movement Index

**What It Is:**
Raw directional movement before smoothing into ADX.

**Formula:**
```
DX = 100 × |+DI - -DI| / (+DI + -DI)
```

**Best Use:**
- More responsive than ADX
- Early trend detection
- Combine with ADX for confirmation

---

## 4.8 PLUS_DI (+DI) - Plus Directional Indicator

**What It Is:**
Measures upward price movement strength.

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| +DI > -DI | Bullish pressure dominant |
| +DI rising | Increasing bullish momentum |
| +DI > 25 | Significant bullish movement |

**Key Signal:**
- +DI crosses above -DI with ADX > 20 → BUY signal

---

## 4.9 MINUS_DI (-DI) - Minus Directional Indicator

**What It Is:**
Measures downward price movement strength.

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| -DI > +DI | Bearish pressure dominant |
| -DI rising | Increasing bearish momentum |
| -DI > 25 | Significant bearish movement |

**Key Signal:**
- -DI crosses above +DI with ADX > 20 → SELL signal

---

## 4.10 PLUS_DM (+DM) - Plus Directional Movement

**What It Is:**
Raw upward directional movement (before smoothing).

**Formula:**
```
+DM = High - Previous High (if positive and > -DM, else 0)
```

**Best Use:**
- Building custom indicators
- Understanding DI calculation

---

## 4.11 MINUS_DM (-DM) - Minus Directional Movement

**What It Is:**
Raw downward directional movement (before smoothing).

**Formula:**
```
-DM = Previous Low - Low (if positive and > +DM, else 0)
```

---

## 4.12 AROON - Aroon Indicator

**Creator:** Tushar Chande (1995)

**What It Is:**
Measures time since highest high and lowest low.

**Components:**
```
Aroon Up = ((Period - Days Since Highest High) / Period) × 100
Aroon Down = ((Period - Days Since Lowest Low) / Period) × 100
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| Aroon Up > 70 | Strong uptrend |
| Aroon Down > 70 | Strong downtrend |
| Aroon Up > Aroon Down | Bullish |
| Aroon Down > Aroon Up | Bearish |
| Both < 50 | Consolidation |

**Key Signals:**
- Aroon Up crosses above Aroon Down → Bullish
- Aroon Down crosses above Aroon Up → Bearish

---

## 4.13 AROONOSC - Aroon Oscillator

**What It Is:**
Difference between Aroon Up and Aroon Down.

**Formula:**
```
AROONOSC = Aroon Up - Aroon Down
```

**Interpretation:**
| Value | Meaning |
|-------|---------|
| > 50 | Strong uptrend |
| > 0 | Bullish bias |
| < 0 | Bearish bias |
| < -50 | Strong downtrend |

---

## 4.14 CCI - Commodity Channel Index

**Creator:** Donald Lambert (1980)

**What It Is:**
Measures price deviation from statistical mean.

**Formula:**
```
CCI = (Typical Price - SMA(TP)) / (0.015 × Mean Deviation)
Typical Price = (High + Low + Close) / 3
```

**Interpretation:**
| CCI Value | Condition |
|-----------|-----------|
| > +100 | Overbought |
| +100 to -100 | Normal range |
| < -100 | Oversold |
| > +200 | Extremely overbought |
| < -200 | Extremely oversold |

**Context-Aware Usage:**
- In UPTREND: CCI > +100 is strength, not sell signal
- In DOWNTREND: CCI < -100 is strength, not buy signal
- In RANGING: Trade reversals at ±100

---

## 4.15 CMO - Chande Momentum Oscillator

**Creator:** Tushar Chande

**What It Is:**
Similar to RSI but uses raw momentum, not smoothed.

**Formula:**
```
CMO = 100 × (Sum of Up Days - Sum of Down Days) / (Sum of Up Days + Sum of Down Days)
```

**Interpretation:**
| CMO Value | Condition |
|-----------|-----------|
| > +50 | Overbought |
| < -50 | Oversold |
| Crossing 0 | Momentum shift |

**Difference from RSI:**
- More volatile than RSI
- Faster signals
- More prone to whipsaws

---

## 4.16 MOM - Momentum

**What It Is:**
Simple price change over n periods.

**Formula:**
```
MOM = Close - Close[n periods ago]
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| MOM > 0 | Price higher than n periods ago |
| MOM < 0 | Price lower than n periods ago |
| MOM rising | Accelerating momentum |
| MOM falling | Decelerating momentum |

---

## 4.17 ROC - Rate of Change

**What It Is:**
Percentage change over n periods.

**Formula:**
```
ROC = ((Close - Close[n]) / Close[n]) × 100
```

**Interpretation:**
- Positive ROC: Bullish momentum
- Negative ROC: Bearish momentum
- Extreme values: Potential reversal

---

## 4.18 ROCP - Rate of Change Percentage

**What It Is:**
ROC expressed as decimal (not percentage).

**Formula:**
```
ROCP = (Close - Close[n]) / Close[n]
```

---

## 4.19 ROCR - Rate of Change Ratio

**What It Is:**
Price ratio over n periods.

**Formula:**
```
ROCR = Close / Close[n]
```

**Interpretation:**
- ROCR > 1: Price increased
- ROCR < 1: Price decreased
- ROCR = 1: No change

---

## 4.20 ROCR100 - Rate of Change Ratio × 100

**What It Is:**
ROCR scaled by 100 for easier reading.

**Formula:**
```
ROCR100 = (Close / Close[n]) × 100
```

**Interpretation:**
- ROCR100 > 100: Price increased
- ROCR100 < 100: Price decreased

---

## 4.21 STOCH - Stochastic Oscillator

**Creator:** George Lane (1950s)

**What It Is:**
Compares closing price to price range over period.

**Components:**
```
%K = 100 × (Close - Lowest Low) / (Highest High - Lowest Low)
%D = SMA(3) of %K
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| %K > 80 | Overbought |
| %K < 20 | Oversold |
| %K > %D | Bullish momentum |
| %K < %D | Bearish momentum |

**Key Signals:**
- %K crosses above %D in oversold → BUY
- %K crosses below %D in overbought → SELL

**Context-Aware Usage:**
- In UPTREND: Oversold is buying opportunity
- In DOWNTREND: Overbought is shorting opportunity
- In RANGING: Trade both extremes

---

## 4.22 STOCHF - Stochastic Fast

**What It Is:**
Unsmoothed stochastic (raw %K and %D).

**Interpretation:**
- More responsive than regular Stochastic
- More whipsaws
- Better for scalping

---

## 4.23 STOCHRSI - Stochastic RSI

**What It Is:**
Stochastic formula applied to RSI values.

**Formula:**
```
StochRSI = (RSI - Lowest RSI) / (Highest RSI - Lowest RSI)
```

**Interpretation:**
- More sensitive than RSI alone
- Faster signals
- Good for catching momentum shifts

---

## 4.24 APO - Absolute Price Oscillator

**What It Is:**
Difference between two EMAs (absolute, not percentage).

**Formula:**
```
APO = EMA(fast) - EMA(slow)
```

**Interpretation:**
- APO > 0: Bullish
- APO < 0: Bearish
- Similar to MACD line

---

## 4.25 PPO - Percentage Price Oscillator

**What It Is:**
Difference between two EMAs as percentage.

**Formula:**
```
PPO = ((EMA(fast) - EMA(slow)) / EMA(slow)) × 100
```

**Advantage over MACD:**
- Comparable across different price levels
- Better for comparing securities

---

## 4.26 BOP - Balance of Power

**What It Is:**
Measures buying vs selling pressure.

**Formula:**
```
BOP = (Close - Open) / (High - Low)
```

**Interpretation:**
| BOP Value | Meaning |
|-----------|---------|
| > 0 | Buyers in control |
| < 0 | Sellers in control |
| Near +1 | Strong buying |
| Near -1 | Strong selling |

---

## 4.27 IMI - Intraday Momentum Index

**What It Is:**
RSI-like indicator using open-close relationship.

**Formula:**
```
IMI = 100 × (Sum of Gains) / (Sum of Gains + Sum of Losses)
Where Gain = Close - Open (if positive)
```

**Interpretation:**
- IMI > 70: Overbought
- IMI < 30: Oversold
- Better for intraday analysis

---

## 4.28 MFI - Money Flow Index

**What It Is:**
Volume-weighted RSI.

**Formula:**
```
MFI = 100 - (100 / (1 + Money Flow Ratio))
Money Flow Ratio = Positive Money Flow / Negative Money Flow
```

**Interpretation:**
| MFI Value | Condition |
|-----------|-----------|
| > 80 | Overbought |
| < 20 | Oversold |

**Key Insight:**
- Includes volume, unlike RSI
- Divergence with price is significant
- Better for stocks than forex

---

## 4.29 TRIX - Triple Smooth EMA Rate of Change

**What It Is:**
Rate of change of triple-smoothed EMA.

**Formula:**
```
TRIX = ROC(EMA(EMA(EMA(Close))))
```

**Interpretation:**
- TRIX > 0: Bullish
- TRIX < 0: Bearish
- Very smooth, filters noise
- Good for identifying major trends

**Key Signal:**
- TRIX crossing zero → Major trend change

---

## 4.30 ULTOSC - Ultimate Oscillator

**Creator:** Larry Williams (1976)

**What It Is:**
Combines three timeframes to reduce false signals.

**Formula:**
```
ULTOSC = 100 × [(4×BP7/TR7) + (2×BP14/TR14) + (BP28/TR28)] / 7
BP = Buying Pressure = Close - Min(Low, Previous Close)
TR = True Range
```

**Interpretation:**
| ULTOSC Value | Condition |
|--------------|-----------|
| > 70 | Overbought |
| < 30 | Oversold |

**Key Insight:**
- Less prone to false signals than single-period oscillators
- Divergence is particularly significant

---

## 4.31 WILLR - Williams %R

**Creator:** Larry Williams

**What It Is:**
Inverse of Stochastic %K.

**Formula:**
```
%R = -100 × (Highest High - Close) / (Highest High - Lowest Low)
```

**Interpretation:**
| %R Value | Condition |
|----------|-----------|
| -20 to 0 | Overbought |
| -100 to -80 | Oversold |

**Note:** Scale is inverted (0 at top, -100 at bottom)



================================================================================

# 5. VOLUME INDICATORS (3 INDICATORS)

## Overview
Volume indicators confirm price movements. Volume should CONFIRM the trend.
Rising prices with rising volume = Strong trend
Rising prices with falling volume = Weak trend, potential reversal

---

## 5.1 AD - Accumulation/Distribution Line

**Creator:** Marc Chaikin

**What It Is:**
Cumulative indicator measuring money flow based on close position within range.

**Formula:**
```
CLV = ((Close - Low) - (High - Close)) / (High - Low)
AD = Previous AD + (CLV × Volume)
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| AD rising | Accumulation (buying pressure) |
| AD falling | Distribution (selling pressure) |
| AD rising + Price rising | Confirmed uptrend |
| AD falling + Price falling | Confirmed downtrend |
| AD rising + Price falling | Bullish divergence (reversal warning) |
| AD falling + Price rising | Bearish divergence (reversal warning) |

**Key Insight:**
- Divergence between AD and price is a powerful reversal signal
- AD leads price in many cases

---

## 5.2 ADOSC - Chaikin A/D Oscillator

**Creator:** Marc Chaikin

**What It Is:**
MACD applied to the Accumulation/Distribution line.

**Formula:**
```
ADOSC = EMA(3) of AD - EMA(10) of AD
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| ADOSC > 0 | Accumulation momentum |
| ADOSC < 0 | Distribution momentum |
| ADOSC rising | Increasing buying pressure |
| ADOSC falling | Increasing selling pressure |

**Key Signals:**
- ADOSC crossing zero → Momentum shift
- Divergence with price → Reversal warning

---

## 5.3 OBV - On Balance Volume

**Creator:** Joseph Granville (1963)

**What It Is:**
Cumulative volume that adds on up days, subtracts on down days.

**Formula:**
```
If Close > Previous Close: OBV = Previous OBV + Volume
If Close < Previous Close: OBV = Previous OBV - Volume
If Close = Previous Close: OBV = Previous OBV
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| OBV rising | Volume flowing into security |
| OBV falling | Volume flowing out of security |
| OBV rising + Price rising | Confirmed uptrend |
| OBV falling + Price falling | Confirmed downtrend |
| OBV rising + Price flat | Accumulation, breakout coming |
| OBV falling + Price flat | Distribution, breakdown coming |

**Key Insight:**
- OBV often leads price
- Divergence is a powerful signal
- OBV breakout before price breakout = Strong signal

================================================================================

# 6. VOLATILITY INDICATORS (3 INDICATORS)

## Overview
Volatility indicators measure the MAGNITUDE of price movements.
High volatility = Large price swings, wider stops needed
Low volatility = Small price swings, potential breakout coming

---

## 6.1 ATR - Average True Range

**Creator:** J. Welles Wilder Jr. (1978)

**What It Is:**
Average of True Range over n periods.

**Formula:**
```
True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
ATR = Wilder's Smoothed Average of TR
```

**Interpretation:**
| Condition | Meaning |
|-----------|---------|
| ATR rising | Volatility increasing |
| ATR falling | Volatility decreasing |
| ATR high | Large price swings expected |
| ATR low | Small price swings, squeeze forming |

**Practical Uses:**
- **Stop Loss:** Place stops 1.5-3 × ATR from entry
- **Position Sizing:** Smaller positions when ATR is high
- **Breakout Confirmation:** ATR expansion confirms breakout

**ATR-Based Stop Loss:**
```
Long Stop = Entry - (2 × ATR)
Short Stop = Entry + (2 × ATR)
```

---

## 6.2 NATR - Normalized Average True Range

**What It Is:**
ATR expressed as percentage of closing price.

**Formula:**
```
NATR = (ATR / Close) × 100
```

**Interpretation:**
| NATR Value | Volatility Level |
|------------|------------------|
| < 0.5% | Very low (squeeze) |
| 0.5-1.0% | Normal |
| 1.0-2.0% | High |
| > 2.0% | Extreme (caution) |

**Advantage over ATR:**
- Comparable across different price levels
- Better for comparing volatility between securities

---

## 6.3 TRANGE - True Range

**What It Is:**
Single-period volatility measure.

**Formula:**
```
TRANGE = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
```

**Interpretation:**
- Raw volatility for current bar
- Spikes indicate significant price movement
- Used to calculate ATR

================================================================================

# 7. CYCLE INDICATORS (5 INDICATORS)

## Overview
Cycle indicators use Hilbert Transform to identify market cycles.
They help determine if the market is trending or cycling (ranging).

---

## 7.1 HT_DCPERIOD - Hilbert Transform Dominant Cycle Period

**What It Is:**
Identifies the dominant cycle length in the market.

**Interpretation:**
| Period | Meaning |
|--------|---------|
| 10-20 | Short cycle (fast trading) |
| 20-40 | Medium cycle (swing trading) |
| 40+ | Long cycle (position trading) |

**Best Use:**
- Adaptive indicator periods
- Identifying optimal trading timeframe
- Cycle-based entry timing

---

## 7.2 HT_DCPHASE - Hilbert Transform Dominant Cycle Phase

**What It Is:**
Current phase within the dominant cycle (0-360 degrees).

**Interpretation:**
| Phase | Cycle Position |
|-------|----------------|
| 0° | Cycle bottom |
| 90° | Rising phase |
| 180° | Cycle top |
| 270° | Falling phase |

**Best Use:**
- Timing entries within cycles
- Identifying cycle tops and bottoms
- Combine with HT_DCPERIOD

---

## 7.3 HT_PHASOR - Hilbert Transform Phasor Components

**What It Is:**
Returns InPhase and Quadrature components of the cycle.

**Components:**
- **InPhase:** Real component of cycle
- **Quadrature:** Imaginary component (90° shifted)

**Interpretation:**
- Used to calculate cycle phase
- Advanced cycle analysis
- Building custom cycle indicators

---

## 7.4 HT_SINE - Hilbert Transform SineWave

**What It Is:**
Sine and LeadSine of the dominant cycle.

**Components:**
- **Sine:** Current cycle position as sine wave
- **LeadSine:** Sine shifted forward (leading indicator)

**Interpretation:**
| Condition | Signal |
|-----------|--------|
| Sine crosses above LeadSine | Cycle bottom, BUY |
| Sine crosses below LeadSine | Cycle top, SELL |

**Best Use:**
- Cycle-based trading
- Timing entries at cycle extremes
- Works best in ranging markets

---

## 7.5 HT_TRENDMODE - Hilbert Transform Trend vs Cycle Mode

**What It Is:**
Binary indicator: 1 = Trending, 0 = Cycling (Ranging)

**Interpretation:**
| Value | Market Mode | Strategy |
|-------|-------------|----------|
| 1 | TRENDING | Use trend-following strategies |
| 0 | CYCLING | Use mean-reversion strategies |

**CRITICAL IMPORTANCE:**
This indicator tells you WHICH TYPE of strategy to use!

**Best Use:**
- Strategy selection
- Regime detection
- Combine with ADX for confirmation

================================================================================

# 8. PRICE TRANSFORM (5 INDICATORS)

## Overview
Price transform functions create alternative price representations
that can be used as inputs to other indicators.

---

## 8.1 AVGPRICE - Average Price

**What It Is:**
Simple average of OHLC prices.

**Formula:**
```
AVGPRICE = (Open + High + Low + Close) / 4
```

**Interpretation:**
- Represents "fair value" for the bar
- Smoother than close alone
- Good input for other indicators

---

## 8.2 MEDPRICE - Median Price

**What It Is:**
Midpoint of high and low.

**Formula:**
```
MEDPRICE = (High + Low) / 2
```

**Interpretation:**
- Represents price equilibrium
- Ignores open and close
- Good for range analysis

---

## 8.3 TYPPRICE - Typical Price

**What It Is:**
Average of high, low, and close.

**Formula:**
```
TYPPRICE = (High + Low + Close) / 3
```

**Interpretation:**
- Most common alternative price
- Used in CCI calculation
- Weights close equally with range

---

## 8.4 WCLPRICE - Weighted Close Price

**What It Is:**
Close-weighted average price.

**Formula:**
```
WCLPRICE = (High + Low + Close + Close) / 4
```

**Interpretation:**
- Emphasizes closing price
- Good for trend analysis
- Close is most important price

---

## 8.5 AVGDEV - Average Deviation

**What It Is:**
Average absolute deviation from mean.

**Formula:**
```
AVGDEV = Mean(|Price - SMA(Price)|)
```

**Interpretation:**
- Measures price dispersion
- Alternative to standard deviation
- Less sensitive to outliers

================================================================================

# 9. STATISTICAL FUNCTIONS (9 INDICATORS)

## Overview
Statistical functions provide mathematical analysis of price data,
including regression, correlation, and variance measures.

---

## 9.1 LINEARREG - Linear Regression

**What It Is:**
End point of linear regression line.

**Interpretation:**
- Represents the "expected" price based on trend
- Price above LINEARREG: Above trend
- Price below LINEARREG: Below trend

**Best Use:**
- Trend identification
- Mean reversion targets
- Combine with LINEARREG_SLOPE

---

## 9.2 LINEARREG_SLOPE - Linear Regression Slope

**What It Is:**
Slope of the linear regression line.

**Interpretation:**
| Slope | Meaning |
|-------|---------|
| > 0 | Uptrend |
| < 0 | Downtrend |
| ≈ 0 | No trend |
| Large positive | Strong uptrend |
| Large negative | Strong downtrend |

**Best Use:**
- Trend direction and strength
- Combine with ADX
- Regime detection

---

## 9.3 LINEARREG_ANGLE - Linear Regression Angle

**What It Is:**
Angle of regression line in degrees.

**Interpretation:**
| Angle | Trend Strength |
|-------|----------------|
| > 45° | Very strong uptrend |
| 20-45° | Moderate uptrend |
| -20 to 20° | Sideways |
| -45 to -20° | Moderate downtrend |
| < -45° | Very strong downtrend |

**Best Use:**
- Visual trend strength
- Easy to interpret
- Regime classification

---

## 9.4 LINEARREG_INTERCEPT - Linear Regression Intercept

**What It Is:**
Y-intercept of the regression line.

**Best Use:**
- Building regression channels
- Advanced analysis
- Custom indicators

---

## 9.5 STDDEV - Standard Deviation

**What It Is:**
Measures price dispersion from mean.

**Formula:**
```
STDDEV = √(Σ(Price - Mean)² / n)
```

**Interpretation:**
| STDDEV | Volatility |
|--------|------------|
| Low | Low volatility, squeeze |
| High | High volatility |
| Rising | Volatility increasing |
| Falling | Volatility decreasing |

**Best Use:**
- Bollinger Band calculation
- Volatility analysis
- Position sizing

---

## 9.6 VAR - Variance

**What It Is:**
Square of standard deviation.

**Formula:**
```
VAR = Σ(Price - Mean)² / n
```

**Best Use:**
- Statistical analysis
- Volatility measurement
- Risk calculations

---

## 9.7 TSF - Time Series Forecast

**What It Is:**
Linear regression projected forward one period.

**Formula:**
```
TSF = LINEARREG + LINEARREG_SLOPE
```

**Interpretation:**
- Predicts next period's price
- Price above TSF: Bullish
- Price below TSF: Bearish

**Best Use:**
- Short-term forecasting
- Trend confirmation
- Entry timing

---

## 9.8 BETA - Beta Coefficient

**What It Is:**
Measures correlation with benchmark.

**Interpretation:**
| Beta | Meaning |
|------|---------|
| > 1 | More volatile than benchmark |
| = 1 | Same volatility as benchmark |
| < 1 | Less volatile than benchmark |
| < 0 | Inverse correlation |

**Best Use:**
- Portfolio analysis
- Risk assessment
- Hedging decisions

---

## 9.9 CORREL - Pearson Correlation

**What It Is:**
Correlation coefficient between two series.

**Interpretation:**
| CORREL | Relationship |
|--------|--------------|
| +1 | Perfect positive correlation |
| 0 | No correlation |
| -1 | Perfect negative correlation |

**Best Use:**
- Pair trading
- Diversification analysis
- Intermarket analysis



================================================================================

# 10. PATTERN RECOGNITION (61 INDICATORS)

## Overview
Candlestick patterns are visual representations of market psychology.
They indicate potential reversals or continuations based on price action.

**Pattern Values:**
- **+100 to +200:** Bullish pattern detected
- **-100 to -200:** Bearish pattern detected
- **0:** No pattern detected

**Pattern Strength:**
- **±100:** Standard pattern
- **±200:** Strong/confirmed pattern

---

## REVERSAL PATTERNS (Bullish)

### CDL3WHITESOLDIERS - Three White Soldiers
**Pattern:** Three consecutive long bullish candles
**Signal:** STRONG BULLISH reversal
**Context:** Most reliable after downtrend
**Strength:** +100

### CDLMORNINGSTAR - Morning Star
**Pattern:** Bearish candle → Small body → Bullish candle
**Signal:** BULLISH reversal
**Context:** Appears at bottom of downtrend
**Strength:** +100

### CDLMORNINGDOJISTAR - Morning Doji Star
**Pattern:** Bearish candle → Doji → Bullish candle
**Signal:** STRONG BULLISH reversal
**Context:** Doji shows indecision before reversal
**Strength:** +100

### CDLHAMMER - Hammer
**Pattern:** Small body at top, long lower shadow
**Signal:** BULLISH reversal
**Context:** Must appear after downtrend
**Strength:** +100

### CDLINVERTEDHAMMER - Inverted Hammer
**Pattern:** Small body at bottom, long upper shadow
**Signal:** BULLISH reversal (needs confirmation)
**Context:** After downtrend, needs next candle confirmation
**Strength:** +100

### CDLENGULFING - Engulfing Pattern
**Pattern:** Current candle body engulfs previous
**Signal:** Bullish (+100) or Bearish (-100)
**Context:** Strong reversal signal
**Strength:** ±100

### CDLPIERCING - Piercing Pattern
**Pattern:** Bearish candle → Bullish candle closing above midpoint
**Signal:** BULLISH reversal
**Context:** After downtrend
**Strength:** +100

### CDLHARAMI - Harami
**Pattern:** Large candle → Small candle inside
**Signal:** Potential reversal
**Context:** Needs confirmation
**Strength:** ±100

### CDLHARAMICROSS - Harami Cross
**Pattern:** Large candle → Doji inside
**Signal:** STRONGER reversal than regular Harami
**Context:** Doji adds significance
**Strength:** ±100

### CDLDOJI - Doji
**Pattern:** Open ≈ Close (cross shape)
**Signal:** INDECISION
**Context:** Potential reversal, needs confirmation
**Strength:** ±100

### CDLDRAGONFLYDOJI - Dragonfly Doji
**Pattern:** Doji with long lower shadow
**Signal:** BULLISH reversal
**Context:** After downtrend
**Strength:** +100

### CDLGRAVESTONEDOJI - Gravestone Doji
**Pattern:** Doji with long upper shadow
**Signal:** BEARISH reversal
**Context:** After uptrend
**Strength:** -100

---

## REVERSAL PATTERNS (Bearish)

### CDL3BLACKCROWS - Three Black Crows
**Pattern:** Three consecutive long bearish candles
**Signal:** STRONG BEARISH reversal
**Context:** Most reliable after uptrend
**Strength:** -100

### CDLEVENINGSTAR - Evening Star
**Pattern:** Bullish candle → Small body → Bearish candle
**Signal:** BEARISH reversal
**Context:** Appears at top of uptrend
**Strength:** -100

### CDLEVENINGDOJISTAR - Evening Doji Star
**Pattern:** Bullish candle → Doji → Bearish candle
**Signal:** STRONG BEARISH reversal
**Context:** Doji shows indecision before reversal
**Strength:** -100

### CDLHANGINGMAN - Hanging Man
**Pattern:** Same as Hammer but after uptrend
**Signal:** BEARISH reversal
**Context:** Must appear after uptrend
**Strength:** -100

### CDLSHOOTINGSTAR - Shooting Star
**Pattern:** Small body at bottom, long upper shadow
**Signal:** BEARISH reversal
**Context:** After uptrend
**Strength:** -100

### CDLDARKCLOUDCOVER - Dark Cloud Cover
**Pattern:** Bullish candle → Bearish candle closing below midpoint
**Signal:** BEARISH reversal
**Context:** After uptrend
**Strength:** -100

---

## CONTINUATION PATTERNS

### CDL3LINESTRIKE - Three Line Strike
**Pattern:** Three candles in direction → Opposite candle engulfing all three
**Signal:** CONTINUATION (despite appearance)
**Context:** Trend continues after pattern
**Strength:** ±100

### CDLRISEFALL3METHODS - Rising/Falling Three Methods
**Pattern:** Long candle → 3 small opposite candles → Long candle same direction
**Signal:** CONTINUATION
**Context:** Pause in trend, then continuation
**Strength:** ±100

### CDLSEPARATINGLINES - Separating Lines
**Pattern:** Opposite color candle opening at same level
**Signal:** CONTINUATION
**Context:** Trend resumes
**Strength:** ±100

### CDLTASUKIGAP - Tasuki Gap
**Pattern:** Gap followed by partial fill
**Signal:** CONTINUATION
**Context:** Gap remains unfilled
**Strength:** ±100

---

## INDECISION PATTERNS

### CDLSPINNINGTOP - Spinning Top
**Pattern:** Small body with upper and lower shadows
**Signal:** INDECISION
**Context:** Potential reversal, needs confirmation
**Strength:** ±100

### CDLHIGHWAVE - High Wave
**Pattern:** Very long shadows, small body
**Signal:** EXTREME INDECISION
**Context:** Major uncertainty
**Strength:** ±100

### CDLLONGLEGGEDDOJI - Long Legged Doji
**Pattern:** Doji with very long shadows
**Signal:** EXTREME INDECISION
**Context:** Battle between bulls and bears
**Strength:** ±100

### CDLRICKSHAWMAN - Rickshaw Man
**Pattern:** Doji with equal long shadows
**Signal:** INDECISION
**Context:** Perfect balance of forces
**Strength:** ±100

---

## STRENGTH PATTERNS

### CDLMARUBOZU - Marubozu
**Pattern:** Full body candle, no shadows
**Signal:** STRONG MOMENTUM
**Context:** Bullish (+100) or Bearish (-100)
**Strength:** ±100

### CDLCLOSINGMARUBOZU - Closing Marubozu
**Pattern:** No shadow on closing end
**Signal:** STRONG MOMENTUM
**Context:** Buyers/sellers in control at close
**Strength:** ±100

### CDLLONGLINE - Long Line Candle
**Pattern:** Very long body
**Signal:** STRONG MOMENTUM
**Context:** Significant price movement
**Strength:** ±100

### CDLSHORTLINE - Short Line Candle
**Pattern:** Very short body
**Signal:** WEAK MOMENTUM
**Context:** Indecision or consolidation
**Strength:** ±100

---

## COMPLEX PATTERNS

### CDLABANDONEDBABY - Abandoned Baby
**Pattern:** Gap → Doji → Gap (opposite direction)
**Signal:** STRONG REVERSAL
**Context:** Rare but powerful
**Strength:** ±100

### CDLTRISTAR - Tri-Star
**Pattern:** Three consecutive Dojis
**Signal:** STRONG REVERSAL
**Context:** Extreme indecision
**Strength:** ±100

### CDLKICKING - Kicking
**Pattern:** Marubozu → Gap → Opposite Marubozu
**Signal:** VERY STRONG REVERSAL
**Context:** One of the strongest patterns
**Strength:** ±100

### CDLKICKINGBYLENGTH - Kicking By Length
**Pattern:** Kicking with length confirmation
**Signal:** VERY STRONG REVERSAL
**Context:** Confirmed by candle length
**Strength:** ±100

---

## ALL 61 CANDLESTICK PATTERNS

| # | Pattern | Type | Signal |
|---|---------|------|--------|
| 1 | CDL2CROWS | Bearish | Reversal |
| 2 | CDL3BLACKCROWS | Bearish | Strong Reversal |
| 3 | CDL3INSIDE | Both | Reversal |
| 4 | CDL3LINESTRIKE | Both | Continuation |
| 5 | CDL3OUTSIDE | Both | Reversal |
| 6 | CDL3STARSINSOUTH | Bullish | Reversal |
| 7 | CDL3WHITESOLDIERS | Bullish | Strong Reversal |
| 8 | CDLABANDONEDBABY | Both | Strong Reversal |
| 9 | CDLADVANCEBLOCK | Bearish | Reversal |
| 10 | CDLBELTHOLD | Both | Reversal |
| 11 | CDLBREAKAWAY | Both | Reversal |
| 12 | CDLCLOSINGMARUBOZU | Both | Momentum |
| 13 | CDLCONCEALBABYSWALL | Bullish | Reversal |
| 14 | CDLCOUNTERATTACK | Both | Reversal |
| 15 | CDLDARKCLOUDCOVER | Bearish | Reversal |
| 16 | CDLDOJI | Neutral | Indecision |
| 17 | CDLDOJISTAR | Both | Reversal |
| 18 | CDLDRAGONFLYDOJI | Bullish | Reversal |
| 19 | CDLENGULFING | Both | Strong Reversal |
| 20 | CDLEVENINGDOJISTAR | Bearish | Strong Reversal |
| 21 | CDLEVENINGSTAR | Bearish | Reversal |
| 22 | CDLGAPSIDESIDEWHITE | Both | Continuation |
| 23 | CDLGRAVESTONEDOJI | Bearish | Reversal |
| 24 | CDLHAMMER | Bullish | Reversal |
| 25 | CDLHANGINGMAN | Bearish | Reversal |
| 26 | CDLHARAMI | Both | Reversal |
| 27 | CDLHARAMICROSS | Both | Strong Reversal |
| 28 | CDLHIGHWAVE | Neutral | Indecision |
| 29 | CDLHIKKAKE | Both | Reversal |
| 30 | CDLHIKKAKEMOD | Both | Reversal |
| 31 | CDLHOMINGPIGEON | Bullish | Reversal |
| 32 | CDLIDENTICAL3CROWS | Bearish | Strong Reversal |
| 33 | CDLINNECK | Bearish | Continuation |
| 34 | CDLINVERTEDHAMMER | Bullish | Reversal |
| 35 | CDLKICKING | Both | Very Strong Reversal |
| 36 | CDLKICKINGBYLENGTH | Both | Very Strong Reversal |
| 37 | CDLLADDERBOTTOM | Bullish | Reversal |
| 38 | CDLLONGLEGGEDDOJI | Neutral | Indecision |
| 39 | CDLLONGLINE | Both | Momentum |
| 40 | CDLMARUBOZU | Both | Strong Momentum |
| 41 | CDLMATCHINGLOW | Bullish | Reversal |
| 42 | CDLMATHOLD | Both | Continuation |
| 43 | CDLMORNINGDOJISTAR | Bullish | Strong Reversal |
| 44 | CDLMORNINGSTAR | Bullish | Reversal |
| 45 | CDLONNECK | Bearish | Continuation |
| 46 | CDLPIERCING | Bullish | Reversal |
| 47 | CDLRICKSHAWMAN | Neutral | Indecision |
| 48 | CDLRISEFALL3METHODS | Both | Continuation |
| 49 | CDLSEPARATINGLINES | Both | Continuation |
| 50 | CDLSHOOTINGSTAR | Bearish | Reversal |
| 51 | CDLSHORTLINE | Neutral | Weak Momentum |
| 52 | CDLSPINNINGTOP | Neutral | Indecision |
| 53 | CDLSTALLEDPATTERN | Bearish | Reversal |
| 54 | CDLSTICKSANDWICH | Bullish | Reversal |
| 55 | CDLTAKURI | Bullish | Reversal |
| 56 | CDLTASUKIGAP | Both | Continuation |
| 57 | CDLTHRUSTING | Bearish | Continuation |
| 58 | CDLTRISTAR | Both | Strong Reversal |
| 59 | CDLUNIQUE3RIVER | Bullish | Reversal |
| 60 | CDLUPSIDEGAP2CROWS | Bearish | Reversal |
| 61 | CDLXSIDEGAP3METHODS | Both | Continuation |

---

## PATTERN INTERPRETATION BY REGIME

| Regime | Bullish Patterns | Bearish Patterns |
|--------|------------------|------------------|
| TRENDING UP | Continuation signals | Ignore or reduce size |
| TRENDING DOWN | Ignore or reduce size | Continuation signals |
| RANGING | Trade at support | Trade at resistance |
| VOLATILE | Unreliable | Unreliable |

**Key Rule:** Patterns are MOST reliable when they align with the regime!



================================================================================

# 11. MATH TRANSFORM (15 FUNCTIONS)

## Overview
Math transform functions apply mathematical operations to price data.
Primarily used for data normalization, custom indicator development,
and advanced analysis.

---

## 11.1 LN - Natural Logarithm

**Formula:** `LN(x) = logₑ(x)`

**Use Cases:**
- Log returns calculation
- Normalizing price data
- Percentage change analysis

**Trading Application:**
```
Log Return = LN(Close / Previous Close)
```

---

## 11.2 LOG10 - Base-10 Logarithm

**Formula:** `LOG10(x) = log₁₀(x)`

**Use Cases:**
- Scale compression
- Order of magnitude analysis
- Custom indicators

---

## 11.3 SQRT - Square Root

**Formula:** `SQRT(x) = √x`

**Use Cases:**
- Volatility calculations
- Standard deviation
- Risk metrics

---

## 11.4 EXP - Exponential

**Formula:** `EXP(x) = eˣ`

**Use Cases:**
- Reverse log transformation
- Growth calculations
- Compound returns

---

## 11.5 CEIL - Ceiling

**Formula:** `CEIL(x) = ⌈x⌉` (round up)

**Use Cases:**
- Price level rounding
- Lot size calculation
- Grid trading levels

---

## 11.6 FLOOR - Floor

**Formula:** `FLOOR(x) = ⌊x⌋` (round down)

**Use Cases:**
- Price level rounding
- Position sizing
- Support levels

---

## 11.7-11.15 TRIGONOMETRIC FUNCTIONS

| Function | Formula | Use Case |
|----------|---------|----------|
| SIN | sin(x) | Cycle analysis |
| COS | cos(x) | Cycle analysis |
| TAN | tan(x) | Angle calculations |
| ASIN | arcsin(x) | Inverse sine |
| ACOS | arccos(x) | Inverse cosine |
| ATAN | arctan(x) | Inverse tangent |
| SINH | sinh(x) | Hyperbolic sine |
| COSH | cosh(x) | Hyperbolic cosine |
| TANH | tanh(x) | Hyperbolic tangent |

**Trading Applications:**
- Cycle-based indicators
- Phase analysis
- Custom oscillators
- Hilbert Transform calculations

================================================================================

# 12. MATH OPERATORS (11 FUNCTIONS)

## Overview
Math operators perform basic mathematical operations on price series.
Used for custom indicator development and price analysis.

---

## 12.1 ADD - Addition

**Formula:** `ADD(a, b) = a + b`

**Use Cases:**
- Combining indicators
- Creating composite signals
- Custom calculations

---

## 12.2 SUB - Subtraction

**Formula:** `SUB(a, b) = a - b`

**Use Cases:**
- Spread calculation
- Difference analysis
- MACD-like indicators

---

## 12.3 MULT - Multiplication

**Formula:** `MULT(a, b) = a × b`

**Use Cases:**
- Scaling indicators
- Volume-weighted calculations
- Position sizing

---

## 12.4 DIV - Division

**Formula:** `DIV(a, b) = a / b`

**Use Cases:**
- Ratio analysis
- Normalization
- Relative strength

---

## 12.5 MAX - Maximum Value

**Formula:** `MAX(series, period)` = Highest value over period

**Trading Applications:**
- Resistance levels
- Donchian Channel upper band
- Highest high analysis

**Interpretation:**
- Price at MAX: Potential resistance
- Breaking MAX: Bullish breakout

---

## 12.6 MAXINDEX - Index of Maximum

**Formula:** Returns the index (bar number) of the maximum value

**Use Cases:**
- Time since high
- Pattern recognition
- Cycle analysis

---

## 12.7 MIN - Minimum Value

**Formula:** `MIN(series, period)` = Lowest value over period

**Trading Applications:**
- Support levels
- Donchian Channel lower band
- Lowest low analysis

**Interpretation:**
- Price at MIN: Potential support
- Breaking MIN: Bearish breakdown

---

## 12.8 MININDEX - Index of Minimum

**Formula:** Returns the index (bar number) of the minimum value

**Use Cases:**
- Time since low
- Pattern recognition
- Cycle analysis

---

## 12.9 MINMAX - Min and Max Together

**Formula:** Returns both minimum and maximum values

**Trading Applications:**
- Range analysis
- Donchian Channels
- Support/Resistance identification

---

## 12.10 MINMAXINDEX - Indices of Min and Max

**Formula:** Returns indices of both minimum and maximum

**Use Cases:**
- Range timing analysis
- Pattern recognition

---

## 12.11 SUM - Summation

**Formula:** `SUM(series, period)` = Sum of values over period

**Trading Applications:**
- Cumulative indicators
- Volume analysis
- Custom calculations

================================================================================

# 13. INDICATOR HIERARCHY & CONFLICT RESOLUTION

## The Decision Hierarchy

When indicators give conflicting signals, follow this priority:

```
┌─────────────────────────────────────────────────────────────┐
│  1. REGIME DETECTION (Highest Priority)                     │
│     ADX, HT_TRENDMODE, AROON, MA Alignment                 │
│     → Determines WHICH strategy to use                      │
├─────────────────────────────────────────────────────────────┤
│  2. TREND DIRECTION                                         │
│     +DI/-DI, MA Slopes, LINEARREG_ANGLE                    │
│     → Determines trade DIRECTION                            │
├─────────────────────────────────────────────────────────────┤
│  3. MOMENTUM CONFIRMATION                                   │
│     RSI, MACD, Stochastic, CCI, CMO                        │
│     → Confirms or warns against trade                       │
├─────────────────────────────────────────────────────────────┤
│  4. VOLUME CONFIRMATION                                     │
│     AD, ADOSC, OBV                                         │
│     → Validates or invalidates signal                       │
├─────────────────────────────────────────────────────────────┤
│  5. PATTERN TIMING (Lowest Priority)                        │
│     Candlestick patterns                                    │
│     → Fine-tunes entry timing                               │
└─────────────────────────────────────────────────────────────┘
```

## Conflict Resolution Rules

### Rule 1: Regime Overrides Everything
If regime says TRENDING UP, ignore bearish momentum signals.
If regime says RANGING, use mean-reversion despite trend indicators.

### Rule 2: Majority Rules Within Category
Count bullish vs bearish signals within each category.
Use the majority direction.

### Rule 3: Volume Confirms or Denies
If volume diverges from price, be cautious.
Volume should confirm the move.

### Rule 4: Patterns Refine, Don't Override
Patterns help with timing, not direction.
A bearish pattern in an uptrend is a pullback, not a reversal.

## Example Conflict Resolution

**Scenario:**
- ADX = 35 (strong trend)
- +DI > -DI (bullish)
- RSI = 75 (overbought)
- MACD > Signal (bullish)
- OBV rising (bullish)
- Shooting Star pattern (bearish)

**Resolution:**
1. Regime: TRENDING UP (ADX > 25, +DI > -DI)
2. Trend: BULLISH (+DI dominant)
3. Momentum: MIXED (RSI overbought, but MACD bullish)
4. Volume: CONFIRMS (OBV rising)
5. Pattern: Bearish (but in uptrend = pullback)

**Decision:** BULLISH BIAS
- RSI overbought in uptrend = strength, not sell
- Shooting Star = potential pullback, not reversal
- Wait for pullback to buy, don't short

================================================================================

# 14. CONTEXT-AWARE INTERPRETATION RULES

## RSI Interpretation by Regime

| Regime | RSI > 70 | RSI < 30 | RSI = 50 |
|--------|----------|----------|----------|
| TRENDING UP | Strength, hold longs | BUY opportunity | Neutral, wait |
| TRENDING DOWN | SELL opportunity | Strength, hold shorts | Neutral, wait |
| RANGING | SELL signal | BUY signal | No trade |
| VOLATILE | Unreliable | Unreliable | Unreliable |

## MACD Interpretation by Regime

| Regime | MACD Cross Up | MACD Cross Down | MACD > 0 |
|--------|---------------|-----------------|----------|
| TRENDING UP | Add to longs | Reduce size | Confirmed |
| TRENDING DOWN | Reduce shorts | Add to shorts | Bounce only |
| RANGING | BUY signal | SELL signal | Bullish bias |
| VOLATILE | Unreliable | Unreliable | Unreliable |

## Bollinger Band Interpretation by Regime

| Regime | Price at Upper | Price at Lower | Squeeze |
|--------|----------------|----------------|---------|
| TRENDING UP | Walking band (bullish) | BUY opportunity | Breakout up likely |
| TRENDING DOWN | SELL opportunity | Walking band (bearish) | Breakout down likely |
| RANGING | SELL signal | BUY signal | Breakout either way |
| VOLATILE | Expansion | Expansion | N/A |

## Stochastic Interpretation by Regime

| Regime | %K > 80 | %K < 20 | %K Cross %D |
|--------|---------|---------|-------------|
| TRENDING UP | Strength | BUY | Timing signal |
| TRENDING DOWN | SELL | Strength | Timing signal |
| RANGING | SELL | BUY | Trade signal |
| VOLATILE | Unreliable | Unreliable | Unreliable |

## Volume Interpretation

| Price Action | Volume Rising | Volume Falling |
|--------------|---------------|----------------|
| Price Rising | CONFIRMED uptrend | WEAK uptrend, caution |
| Price Falling | CONFIRMED downtrend | WEAK downtrend, caution |
| Price Flat | Accumulation/Distribution | No interest |

## Pattern Interpretation by Regime

| Regime | Bullish Pattern | Bearish Pattern |
|--------|-----------------|-----------------|
| TRENDING UP | Continuation, BUY | Pullback, wait |
| TRENDING DOWN | Bounce, wait | Continuation, SELL |
| RANGING | BUY at support | SELL at resistance |
| VOLATILE | Unreliable | Unreliable |

================================================================================

# QUICK REFERENCE CARD

## Regime Detection Checklist

**TRENDING UP:**
- [ ] ADX > 25
- [ ] +DI > -DI
- [ ] Price > SMA(50) > SMA(200)
- [ ] HT_TRENDMODE = 1
- [ ] AROON Up > 70

**TRENDING DOWN:**
- [ ] ADX > 25
- [ ] -DI > +DI
- [ ] Price < SMA(50) < SMA(200)
- [ ] HT_TRENDMODE = 1
- [ ] AROON Down > 70

**RANGING:**
- [ ] ADX < 20
- [ ] +DI ≈ -DI
- [ ] MAs flat and intertwined
- [ ] HT_TRENDMODE = 0
- [ ] AROON oscillating

**VOLATILE:**
- [ ] NATR > 1.0%
- [ ] ATR spiking
- [ ] Wide Bollinger Bands
- [ ] Erratic price action

## Trade Decision Flowchart

```
1. What is the REGIME?
   ├── TRENDING UP → Only look for LONGS
   ├── TRENDING DOWN → Only look for SHORTS
   ├── RANGING → Trade both directions at extremes
   └── VOLATILE → Reduce size or stay out

2. What is the TREND saying?
   ├── Bullish (MAs aligned up) → Confirms long bias
   └── Bearish (MAs aligned down) → Confirms short bias

3. What is MOMENTUM saying?
   ├── Confirms trend → Proceed with trade
   └── Diverges from trend → Caution, reduce size

4. What is VOLUME saying?
   ├── Confirms price action → Strong signal
   └── Diverges from price → Weak signal, caution

5. What are PATTERNS saying?
   ├── Aligns with regime → Good entry timing
   └── Conflicts with regime → Ignore or wait
```

================================================================================

# DOCUMENT END

**Version:** 1.0
**Last Updated:** January 2026
**Total Indicators Documented:** 161

This knowledge base should be used by the Wisdom Engine to make
INTELLIGENT, CONTEXT-AWARE trading decisions based on COMPLETE
market understanding, not simple scoring.

