"""
Kuiper V2 Data Models
=====================
Data classes for market analysis, trade decisions, and results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class MarketRegime(Enum):
    """Market regime classification."""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"


class TradeDirection(Enum):
    """Trade direction."""
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"


@dataclass
class RegimeAnalysis:
    """Result of market regime detection."""
    regime: MarketRegime
    adx_value: float
    adx_interpretation: str
    trend_mode: int  # HT_TRENDMODE: 0=cycle, 1=trend
    trend_mode_interpretation: str
    ma_alignment: str  # "BULLISH", "BEARISH", "MIXED"
    ma_alignment_interpretation: str
    volatility_state: str  # "NORMAL", "HIGH", "SPIKE"
    volatility_interpretation: str
    reasoning: str  # Full explanation of regime determination


@dataclass
class TrendAnalysis:
    """Analysis of trend indicators."""
    direction: str  # "UP", "DOWN", "NEUTRAL"
    strength: str  # "STRONG", "MODERATE", "WEAK"
    ma_positions: Dict[str, str]  # e.g., {"SMA_20": "ABOVE_PRICE", ...}
    ema_crossover: str  # "BULLISH", "BEARISH", "NONE"
    interpretation: str


@dataclass
class MomentumAnalysis:
    """Analysis of momentum indicators."""
    rsi_value: float
    rsi_interpretation: str
    macd_state: str  # "BULLISH", "BEARISH", "NEUTRAL"
    macd_interpretation: str
    stoch_state: str  # "OVERBOUGHT", "OVERSOLD", "NEUTRAL"
    stoch_interpretation: str
    overall_momentum: str  # "BULLISH", "BEARISH", "NEUTRAL"
    interpretation: str


@dataclass
class VolumeAnalysis:
    """Analysis of volume indicators."""
    obv_trend: str  # "RISING", "FALLING", "FLAT"
    ad_trend: str  # "ACCUMULATION", "DISTRIBUTION", "NEUTRAL"
    confirms_price: bool
    interpretation: str


@dataclass
class PatternAnalysis:
    """Analysis of candlestick patterns."""
    bullish_patterns: List[str]
    bearish_patterns: List[str]
    strongest_pattern: Optional[str]
    pattern_bias: str  # "BULLISH", "BEARISH", "NEUTRAL"
    interpretation: str


@dataclass
class CycleAnalysis:
    """Analysis of cycle indicators."""
    dominant_period: float
    phase: float
    trend_mode: int
    interpretation: str


@dataclass
class IndicatorInterpretations:
    """Complete interpretation of all indicator categories."""
    trend: TrendAnalysis
    momentum: MomentumAnalysis
    volume: VolumeAnalysis
    patterns: PatternAnalysis
    cycles: CycleAnalysis
    
    def get_consensus(self) -> str:
        """Get overall consensus from all interpretations."""
        bullish_count = 0
        bearish_count = 0
        
        # Trend
        if self.trend.direction == "UP":
            bullish_count += 2  # Trend weighted higher
        elif self.trend.direction == "DOWN":
            bearish_count += 2
        
        # Momentum
        if self.momentum.overall_momentum == "BULLISH":
            bullish_count += 1
        elif self.momentum.overall_momentum == "BEARISH":
            bearish_count += 1
        
        # Volume
        if self.volume.confirms_price:
            if self.trend.direction == "UP":
                bullish_count += 1
            elif self.trend.direction == "DOWN":
                bearish_count += 1
        
        # Patterns
        if self.patterns.pattern_bias == "BULLISH":
            bullish_count += 1
        elif self.patterns.pattern_bias == "BEARISH":
            bearish_count += 1
        
        if bullish_count > bearish_count + 1:
            return "BULLISH"
        elif bearish_count > bullish_count + 1:
            return "BEARISH"
        else:
            return "NEUTRAL"


@dataclass
class TradeDecision:
    """Trading decision with full reasoning."""
    direction: TradeDirection
    confidence_factors: List[str]  # What supports this decision
    warning_factors: List[str]  # What to watch out for
    reasoning: str  # Full explanation
    position_size_multiplier: float  # 0.0 to 1.0


@dataclass
class TradeParameters:
    """Calculated trade entry/exit parameters."""
    entry_price: float
    stop_loss: float
    take_profit: float
    stop_loss_pips: float
    take_profit_pips: float
    risk_reward_ratio: float
    atr_value: float
    position_size: float  # Lot size
    entry_reasoning: str
    sl_reasoning: str
    tp_reasoning: str


@dataclass
class MarketAnalysis:
    """Complete market analysis result."""
    symbol: str
    timeframe: str
    timestamp: datetime
    
    # Regime
    regime: MarketRegime
    regime_analysis: RegimeAnalysis
    
    # Interpretations
    interpretations: IndicatorInterpretations
    
    # Decision
    decision: TradeDecision
    
    # Trade parameters (if trade)
    parameters: Optional[TradeParameters]
    
    # Raw indicators for reference
    all_indicators: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "regime": self.regime.value,
            "regime_reasoning": self.regime_analysis.reasoning,
            "decision": self.decision.direction.value,
            "decision_reasoning": self.decision.reasoning,
            "confidence_factors": self.decision.confidence_factors,
            "warning_factors": self.decision.warning_factors,
            "position_size_multiplier": self.decision.position_size_multiplier,
            "entry_price": self.parameters.entry_price if self.parameters else None,
            "stop_loss": self.parameters.stop_loss if self.parameters else None,
            "take_profit": self.parameters.take_profit if self.parameters else None,
            "risk_reward_ratio": self.parameters.risk_reward_ratio if self.parameters else None,
            "interpretations": {
                "trend": self.interpretations.trend.interpretation,
                "momentum": self.interpretations.momentum.interpretation,
                "volume": self.interpretations.volume.interpretation,
                "patterns": self.interpretations.patterns.interpretation,
                "cycles": self.interpretations.cycles.interpretation,
            }
        }


@dataclass
class TradeResult:
    """Result of trade execution."""
    success: bool
    order_id: Optional[str]
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    lot_size: float
    error_message: Optional[str]
    timestamp: datetime
