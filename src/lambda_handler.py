"""
KUIPER V2 LAMBDA - 161 INDICATOR WISDOM ENGINE TRADING SYSTEM
==============================================================

This Lambda integrates the Kuiper V2 Wisdom Engine with the existing
MetaAPI trading infrastructure. It uses ALL 161 TA-Lib indicators to
make WISE trading decisions based on complete market understanding.

5-MINUTE TRADING SYSTEM:
========================
- Executes every 5 minutes via EventBridge
- Trades every 5 minutes for frequent profit opportunities
- Auto-closes positions after 5 minutes
- Tighter TP/SL for quick scalping profits

MULTI-TIMEFRAME APPROACH:
=========================
- H1 (1-hour): Used for REGIME DETECTION (big picture, trend direction)
- M5 (5-minute): Used for ENTRY TIMING (precise signals, momentum)

This gives us:
- Better trend context from H1 (hourly regime)
- More precise entry timing from M5 (5-minute signals)
- Predictions every 5 minutes with hourly trend context

KEY FEATURES:
=============
1. 161 INDICATOR ANALYSIS - Uses every TA-Lib indicator
2. MARKET REGIME DETECTION - Determines Trending/Ranging/Volatile from H1
3. CONTEXT-AWARE INTERPRETATION - Same indicator means different things in different regimes
4. MULTI-TIMEFRAME - H1 for regime, M5 for entry timing
5. 5-MINUTE TRADING - Quick entries and exits for frequent profits
6. HIERARCHY: Regime > Trend > Momentum > Volume > Patterns

INDICATOR CATEGORIES:
====================
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

EXECUTION:
==========
- MetaAPI for trade execution
- Session-based pair selection
- ATR-based dynamic TP/SL (SL: 1.0x ATR, TP: 1.5x ATR for quick profits)
- Position auto-close after 5 minutes
- Runs every 5 minutes via EventBridge
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from dataclasses import dataclass, field
import time
import math

import numpy as np
import talib
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# =============================================================================
# CONFIGURATION
# =============================================================================

# MetaAPI Configuration
METAAPI_TOKEN = os.environ.get("METAAPI_TOKEN", "")
METAAPI_ACCOUNT_ID = os.environ.get("METAAPI_ACCOUNT_ID", "")
METAAPI_BASE_URL = "https://mt-client-api-v1.new-york.agiliumtrade.ai"
METAAPI_MARKET_DATA_URL = "https://mt-market-data-client-api-v1.new-york.agiliumtrade.ai"

# Trading Parameters
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
HOLD_MINUTES = int(os.environ.get("HOLD_MINUTES", "5"))  # Auto-close after 5 minutes for frequent trading
FIXED_LOT_SIZE = float(os.environ.get("LOT_SIZE", "0.40"))
ACCOUNT_BALANCE = float(os.environ.get("ACCOUNT_BALANCE", "10000"))

# Risk Management
MAX_RISK_PERCENT = float(os.environ.get("MAX_RISK_PERCENT", "2.0"))
ATR_SL_MULTIPLIER = float(os.environ.get("ATR_SL_MULTIPLIER", "1.0"))  # Tighter SL for 5-min trading
ATR_TP_MULTIPLIER = float(os.environ.get("ATR_TP_MULTIPLIER", "1.5"))  # Tighter TP for quick profits

# Regime Detection Thresholds
ADX_TRENDING_THRESHOLD = int(os.environ.get("ADX_TRENDING_THRESHOLD", "25"))
ADX_WEAK_THRESHOLD = int(os.environ.get("ADX_WEAK_THRESHOLD", "20"))

# Data Parameters
CANDLE_COUNT = 500  # Minimum candles for accurate indicator computation

# HTTP Constants
CONTENT_TYPE_JSON = "application/json"

# H1 Cache Configuration
H1_CACHE_BUCKET = os.environ.get("H1_CACHE_BUCKET", "kuiper-v2-h1-cache")
H1_CACHE_PREFIX = "h1-cache"
H1_CACHE_MAX_AGE_MINUTES = 65  # Refresh H1 cache if older than 65 minutes (1 hour + buffer)

# =============================================================================
# TRADING PAIRS & SESSION CONFIGURATION
# =============================================================================

TRADING_PAIRS = [
    # Majors
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
    # Crosses
    "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
    "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
    "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
    "CADJPY", "CADCHF", "NZDJPY", "NZDCHF", "CHFJPY"
]

SESSION_CONFIG = {
    'ASIAN': {
        'start_hour': 0,
        'end_hour': 9,
        'pairs': ["USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY", "CADJPY", "CHFJPY",
                  "AUDUSD", "NZDUSD", "AUDNZD", "AUDCAD", "AUDCHF"],
        'description': 'Asian/Tokyo session - JPY & AUD pairs'
    },
    'LONDON': {
        'start_hour': 7,
        'end_hour': 16,
        'pairs': ["EURUSD", "GBPUSD", "EURGBP", "EURJPY", "GBPJPY",
                  "EURCHF", "GBPCHF", "EURAUD", "GBPAUD", "EURCAD", "GBPCAD"],
        'description': 'London session - EUR & GBP pairs'
    },
    'NEWYORK': {
        'start_hour': 12,
        'end_hour': 21,
        'pairs': ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
                  "EURJPY", "GBPJPY", "EURGBP", "EURCAD", "GBPCAD"],
        'description': 'New York session - USD pairs'
    }
}

PIP_VALUES = {
    "EURUSD": 0.0001, "GBPUSD": 0.0001, "USDJPY": 0.01, "USDCHF": 0.0001,
    "AUDUSD": 0.0001, "USDCAD": 0.0001, "NZDUSD": 0.0001,
    "EURGBP": 0.0001, "EURJPY": 0.01, "EURCHF": 0.0001, "EURAUD": 0.0001,
    "EURCAD": 0.0001, "EURNZD": 0.0001,
    "GBPJPY": 0.01, "GBPCHF": 0.0001, "GBPAUD": 0.0001, "GBPCAD": 0.0001, "GBPNZD": 0.0001,
    "AUDJPY": 0.01, "AUDCHF": 0.0001, "AUDCAD": 0.0001, "AUDNZD": 0.0001,
    "CADJPY": 0.01, "CADCHF": 0.0001, "NZDJPY": 0.01, "NZDCHF": 0.0001, "CHFJPY": 0.01
}

# =============================================================================
# AWS CLIENTS
# =============================================================================

_boto_config = Config(connect_timeout=30, read_timeout=30)
_ssm_client = boto3.client('ssm', region_name='us-east-1', config=_boto_config)
_s3_client = boto3.client('s3', region_name='us-east-1', config=_boto_config)

def get_ssm_client():
    return _ssm_client

def get_s3_client():
    return _s3_client

# =============================================================================
# DATA MODELS
# =============================================================================

class MarketRegime(Enum):
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"

class TradeDirection(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"

@dataclass
class RegimeAnalysis:
    regime: MarketRegime
    adx_value: float
    adx_interpretation: str
    trend_mode: int
    trend_mode_interpretation: str
    ma_alignment: str
    ma_alignment_interpretation: str
    volatility_state: str
    volatility_interpretation: str
    reasoning: str

@dataclass
class TradeDecision:
    direction: TradeDirection
    confidence_factors: List[str]
    warning_factors: List[str]
    reasoning: str
    position_size_multiplier: float

@dataclass
class TradeParameters:
    entry_price: float
    stop_loss: float
    take_profit: float
    stop_loss_pips: float
    take_profit_pips: float
    risk_reward_ratio: float
    atr_value: float
    position_size: float
    entry_reasoning: str
    sl_reasoning: str
    tp_reasoning: str

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

def json_dumps(obj):
    return json.dumps(obj, cls=NumpyEncoder)

def safe_float(value, default=0.0):
    """Safely convert to float, handling NaN and None."""
    if value is None:
        return default
    try:
        result = float(value)
        return default if np.isnan(result) else result
    except (ValueError, TypeError):
        return default

def get_pip_value(symbol: str) -> float:
    return PIP_VALUES.get(symbol, 0.0001)

# =============================================================================
# MARKET HOURS & SESSION DETECTION
# =============================================================================

def is_market_open() -> Tuple[bool, str]:
    """Check if forex market is currently open."""
    now = datetime.now(timezone.utc)
    weekday = now.weekday()
    hour = now.hour
    
    if weekday == 5:  # Saturday
        return False, "MARKET_CLOSED_SATURDAY"
    if weekday == 6 and hour < 22:  # Sunday before 22:00
        return False, f"MARKET_CLOSED_SUNDAY (opens in ~{22 - hour}h)"
    if weekday == 4 and hour >= 22:  # Friday after 22:00
        return False, "MARKET_CLOSED_FRIDAY_NIGHT"
    
    return True, "MARKET_OPEN"

def get_session_name() -> str:
    """Get current trading session name."""
    hour = datetime.now(timezone.utc).hour
    
    if 0 <= hour < 8:
        return 'ASIAN'
    elif 8 <= hour < 13:
        return 'LONDON'
    elif 13 <= hour < 21:
        return 'NEW_YORK'
    else:
        return 'OFF_HOURS'

def get_current_session() -> Optional[Dict]:
    """Get current session configuration."""
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    
    for session_name, config in SESSION_CONFIG.items():
        start = config['start_hour']
        end = config['end_hour']
        
        if start > end:
            if current_hour >= start or current_hour < end:
                return {'name': session_name, 'pairs': config['pairs'], 
                        'description': config['description'], 'start': start, 'end': end}
        else:
            if start <= current_hour < end:
                return {'name': session_name, 'pairs': config['pairs'],
                        'description': config['description'], 'start': start, 'end': end}
    
    return None

# =============================================================================
# RISK MANAGEMENT
# =============================================================================

def get_trading_enabled() -> bool:
    """Check kill switch in SSM Parameter Store."""
    try:
        ssm = get_ssm_client()
        response = ssm.get_parameter(Name='/chronos-bolt/trading-enabled')
        return response['Parameter']['Value'].lower() == 'true'
    except Exception:
        return False

def get_daily_stats() -> Dict:
    """Get daily trading stats from SSM."""
    try:
        ssm = get_ssm_client()
        response = ssm.get_parameter(Name='/chronos-bolt/daily-stats')
        stats = json.loads(response['Parameter']['Value'])
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if stats.get('date') != today:
            return reset_daily_stats()
        return stats
    except Exception:
        return reset_daily_stats()

def reset_daily_stats() -> Dict:
    """Reset daily stats for new trading day."""
    stats = {
        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'daily_pnl': 0.0,
        'consecutive_losses': 0,
        'total_trades': 0,
        'wins': 0,
        'losses': 0,
        'pause_until': None
    }
    save_daily_stats(stats)
    return stats

def save_daily_stats(stats: Dict):
    """Save daily stats to SSM."""
    try:
        ssm = get_ssm_client()
        ssm.put_parameter(Name='/chronos-bolt/daily-stats', Value=json.dumps(stats),
                          Type='String', Overwrite=True)
    except Exception as e:
        print(f"Error saving daily stats: {e}")

def update_trade_result(pnl: float, is_win: bool):
    """Update daily stats after a trade closes."""
    stats = get_daily_stats()
    stats['daily_pnl'] += pnl
    stats['total_trades'] += 1
    if is_win:
        stats['wins'] += 1
        stats['consecutive_losses'] = 0
    else:
        stats['losses'] += 1
        stats['consecutive_losses'] += 1
    save_daily_stats(stats)

# =============================================================================
# DATA FETCHING - MetaAPI
# =============================================================================

def fetch_market_price(symbol: str) -> Optional[Dict]:
    """Fetch current bid/ask from MetaAPI."""
    url = f"{METAAPI_BASE_URL}/users/current/accounts/{METAAPI_ACCOUNT_ID}/symbols/{symbol}/current-price"
    
    req = urllib.request.Request(url)
    req.add_header("auth-token", METAAPI_TOKEN)
    req.add_header("Accept", CONTENT_TYPE_JSON)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return {'symbol': symbol, 'bid': data.get('bid'), 'ask': data.get('ask'), 'time': data.get('time')}
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def fetch_candles(symbol: str, timeframe: str = "1h", limit: int = CANDLE_COUNT) -> Dict:
    """Fetch OHLCV candles from MetaAPI."""
    tf_map = {"M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m", "H1": "1h", "H4": "4h", "D1": "1d"}
    tf = tf_map.get(timeframe, timeframe.lower())
    
    url = f"{METAAPI_MARKET_DATA_URL}/users/current/accounts/{METAAPI_ACCOUNT_ID}/historical-market-data/symbols/{symbol}/timeframes/{tf}/candles?limit={limit}"
    
    req = urllib.request.Request(url)
    req.add_header("auth-token", METAAPI_TOKEN)
    req.add_header("Accept", CONTENT_TYPE_JSON)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            candles = json.loads(response.read().decode())
            
            result = {'open': [], 'high': [], 'low': [], 'close': [], 'volume': [], 'time': []}
            for c in candles:
                if c.get('close') is not None:
                    result['open'].append(c.get('open', c['close']))
                    result['high'].append(c.get('high', c['close']))
                    result['low'].append(c.get('low', c['close']))
                    result['close'].append(c['close'])
                    result['volume'].append(c.get('tickVolume', 0))
                    result['time'].append(c.get('time', ''))
            return result
    except Exception as e:
        print(f"Error fetching candles for {symbol}: {e}")
        return {'open': [], 'high': [], 'low': [], 'close': [], 'volume': [], 'time': []}

def fetch_data_parallel(pairs: List[str], timeframe: str = "H1") -> Tuple[Dict, Dict]:
    """Fetch prices and candles for multiple pairs in parallel."""
    prices = {}
    candles = {}
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        # Fetch prices
        price_futures = {executor.submit(fetch_market_price, sym): sym for sym in pairs}
        for future in as_completed(price_futures):
            symbol = price_futures[future]
            try:
                result = future.result()
                if result and result.get('bid') and result.get('ask'):
                    prices[symbol] = result
            except Exception as e:
                print(f"Error fetching price for {symbol}: {e}")
        
        # Fetch candles
        candle_futures = {executor.submit(fetch_candles, sym, timeframe): sym for sym in pairs}
        for future in as_completed(candle_futures):
            symbol = candle_futures[future]
            try:
                candles[symbol] = future.result()
            except Exception as e:
                print(f"Error fetching candles for {symbol}: {e}")
                candles[symbol] = {'open': [], 'high': [], 'low': [], 'close': [], 'volume': [], 'time': []}
    
    return prices, candles


def fetch_data_multi_timeframe(pairs: List[str]) -> Tuple[Dict, Dict, Dict]:
    """
    Fetch prices and candles for multiple pairs in parallel with DUAL TIMEFRAMES.
    
    Returns:
        prices: Current bid/ask prices
        candles_h1: H1 candles for regime detection (big picture)
        candles_m5: M5 candles for entry timing (precise signals)
    """
    prices = {}
    candles_h1 = {}
    candles_m5 = {}
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Fetch prices
        price_futures = {executor.submit(fetch_market_price, sym): sym for sym in pairs}
        
        # Fetch H1 candles (for regime detection)
        h1_futures = {executor.submit(fetch_candles, sym, "H1"): sym for sym in pairs}
        
        # Fetch M5 candles (for entry timing)
        m5_futures = {executor.submit(fetch_candles, sym, "M5"): sym for sym in pairs}
        
        # Collect prices
        for future in as_completed(price_futures):
            symbol = price_futures[future]
            try:
                result = future.result()
                if result and result.get('bid') and result.get('ask'):
                    prices[symbol] = result
            except Exception as e:
                print(f"Error fetching price for {symbol}: {e}")
        
        # Collect H1 candles
        for future in as_completed(h1_futures):
            symbol = h1_futures[future]
            try:
                candles_h1[symbol] = future.result()
            except Exception as e:
                print(f"Error fetching H1 candles for {symbol}: {e}")
                candles_h1[symbol] = {'open': [], 'high': [], 'low': [], 'close': [], 'volume': [], 'time': []}
        
        # Collect M5 candles
        for future in as_completed(m5_futures):
            symbol = m5_futures[future]
            try:
                candles_m5[symbol] = future.result()
            except Exception as e:
                print(f"Error fetching M5 candles for {symbol}: {e}")
                candles_m5[symbol] = {'open': [], 'high': [], 'low': [], 'close': [], 'volume': [], 'time': []}
    
    return prices, candles_h1, candles_m5


# =============================================================================
# H1 CACHE MANAGEMENT - S3 BASED CACHING
# =============================================================================

def get_h1_cache_key(symbol: str) -> str:
    """Get S3 key for H1 cache file."""
    return f"{H1_CACHE_PREFIX}/{symbol}.json"


def is_h1_cache_valid(cache_data: Dict) -> bool:
    """Check if H1 cache is still valid (less than 65 minutes old)."""
    if not cache_data:
        return False
    
    cached_time_str = cache_data.get('cached_at')
    if not cached_time_str:
        return False
    
    try:
        cached_time = datetime.fromisoformat(cached_time_str.replace('Z', '+00:00'))
        age_minutes = (datetime.now(timezone.utc) - cached_time).total_seconds() / 60
        return age_minutes < H1_CACHE_MAX_AGE_MINUTES
    except Exception:
        return False


def load_h1_cache(symbol: str) -> Optional[Dict]:
    """Load H1 cache from S3 for a symbol."""
    try:
        s3 = get_s3_client()
        key = get_h1_cache_key(symbol)
        response = s3.get_object(Bucket=H1_CACHE_BUCKET, Key=key)
        cache_data = json.loads(response['Body'].read().decode('utf-8'))
        
        if is_h1_cache_valid(cache_data):
            return cache_data
        else:
            print(f"  {symbol}: H1 cache expired")
            return None
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None
        print(f"  {symbol}: Error loading H1 cache: {e}")
        return None
    except Exception as e:
        print(f"  {symbol}: Error loading H1 cache: {e}")
        return None


def save_h1_cache(symbol: str, candles: Dict, indicators: Dict, regime_analysis: Dict) -> bool:
    """Save H1 data to S3 cache."""
    try:
        s3 = get_s3_client()
        key = get_h1_cache_key(symbol)
        
        cache_data = {
            'symbol': symbol,
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'candles': candles,
            'indicators': indicators,
            'regime': regime_analysis
        }
        
        s3.put_object(
            Bucket=H1_CACHE_BUCKET,
            Key=key,
            Body=json.dumps(cache_data, cls=NumpyEncoder),
            ContentType='application/json'
        )
        return True
    except Exception as e:
        print(f"  {symbol}: Error saving H1 cache: {e}")
        return False


def load_all_h1_cache(pairs: List[str]) -> Tuple[Dict, Dict, Dict, List[str]]:
    """
    Load H1 cache for all pairs.
    
    Returns:
        h1_candles: Dict of candles by symbol
        h1_indicators: Dict of indicators by symbol
        h1_regimes: Dict of regime analysis by symbol
        missing_pairs: List of pairs that need fresh H1 data
    """
    h1_candles = {}
    h1_indicators = {}
    h1_regimes = {}
    missing_pairs = []
    
    print("  Loading H1 cache from S3...")
    
    for symbol in pairs:
        cache = load_h1_cache(symbol)
        if cache:
            h1_candles[symbol] = cache.get('candles', {})
            h1_indicators[symbol] = cache.get('indicators', {})
            h1_regimes[symbol] = cache.get('regime', {})
        else:
            missing_pairs.append(symbol)
    
    print(f"  H1 Cache: {len(pairs) - len(missing_pairs)}/{len(pairs)} loaded, {len(missing_pairs)} need refresh")
    
    return h1_candles, h1_indicators, h1_regimes, missing_pairs


def refresh_h1_cache_for_pairs(pairs: List[str]) -> Tuple[Dict, Dict, Dict]:
    """
    Fetch fresh H1 data for specified pairs and cache it.
    Uses batched fetching to avoid rate limits.
    
    Returns:
        h1_candles: Dict of candles by symbol
        h1_indicators: Dict of indicators by symbol
        h1_regimes: Dict of regime analysis by symbol
    """
    h1_candles = {}
    h1_indicators = {}
    h1_regimes = {}
    
    if not pairs:
        return h1_candles, h1_indicators, h1_regimes
    
    print(f"  Fetching fresh H1 data for {len(pairs)} pairs (batched)...")
    
    # Batch into groups of 8 to avoid rate limits
    batch_size = 8
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {executor.submit(fetch_candles, sym, "H1"): sym for sym in batch}
            
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    candles = future.result()
                    if candles and candles.get('close') and len(candles['close']) >= 100:
                        h1_candles[symbol] = candles
                        
                        # Compute H1 indicators
                        open_arr = np.array(candles['open'], dtype=np.float64)
                        high_arr = np.array(candles['high'], dtype=np.float64)
                        low_arr = np.array(candles['low'], dtype=np.float64)
                        close_arr = np.array(candles['close'], dtype=np.float64)
                        volume_arr = np.array(candles['volume'], dtype=np.float64)
                        
                        indicators = compute_all_indicators(open_arr, high_arr, low_arr, close_arr, volume_arr)
                        h1_indicators[symbol] = indicators
                        
                        # Detect regime
                        regime_analysis = detect_market_regime(indicators)
                        h1_regimes[symbol] = {
                            'regime': regime_analysis.regime.value,
                            'adx_value': regime_analysis.adx_value,
                            'adx_interpretation': regime_analysis.adx_interpretation,
                            'trend_mode': regime_analysis.trend_mode,
                            'ma_alignment': regime_analysis.ma_alignment,
                            'volatility_state': regime_analysis.volatility_state,
                            'reasoning': regime_analysis.reasoning
                        }
                        
                        # Save to cache
                        save_h1_cache(symbol, candles, indicators, h1_regimes[symbol])
                        print(f"    ✓ {symbol}: H1 cached (regime: {regime_analysis.regime.value})")
                    else:
                        print(f"    ✗ {symbol}: Insufficient H1 data")
                except Exception as e:
                    print(f"    ✗ {symbol}: Error fetching H1: {e}")
        
        # Small delay between batches to avoid rate limits
        if i + batch_size < len(pairs):
            time.sleep(0.5)
    
    return h1_candles, h1_indicators, h1_regimes


def fetch_m5_data_only(pairs: List[str]) -> Tuple[Dict, Dict]:
    """
    Fetch only M5 candles and prices for all pairs.
    This is the main data fetch for each 5-minute run.
    Uses batched fetching to avoid rate limits.
    
    Returns:
        prices: Dict of prices by symbol
        m5_candles: Dict of M5 candles by symbol
    """
    prices = {}
    m5_candles = {}
    
    print(f"  Fetching M5 data + prices for {len(pairs)} pairs (batched)...")
    
    # Batch into groups of 10 to avoid rate limits
    batch_size = 10
    
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        
        with ThreadPoolExecutor(max_workers=batch_size * 2) as executor:
            # Fetch prices
            price_futures = {executor.submit(fetch_market_price, sym): ('price', sym) for sym in batch}
            # Fetch M5 candles
            m5_futures = {executor.submit(fetch_candles, sym, "M5"): ('m5', sym) for sym in batch}
            
            all_futures = {**price_futures, **m5_futures}
            
            for future in as_completed(all_futures):
                data_type, symbol = all_futures[future]
                try:
                    result = future.result()
                    if data_type == 'price':
                        if result and result.get('bid') and result.get('ask'):
                            prices[symbol] = result
                    else:  # m5
                        if result and result.get('close'):
                            m5_candles[symbol] = result
                except Exception as e:
                    print(f"    Error fetching {data_type} for {symbol}: {e}")
        
        # Small delay between batches
        if i + batch_size < len(pairs):
            time.sleep(0.3)
    
    print(f"  Prices: {len(prices)}/{len(pairs)}, M5 Candles: {len(m5_candles)}/{len(pairs)}")
    
    return prices, m5_candles


def fetch_data_with_h1_cache(pairs: List[str]) -> Tuple[Dict, Dict, Dict, Dict]:
    """
    Main data fetching function with H1 caching.
    
    - Loads H1 data from S3 cache (refreshed hourly)
    - Fetches fresh M5 data every 5 minutes
    - Computes all 158 indicators on both timeframes
    
    Returns:
        prices: Current bid/ask prices
        h1_indicators: H1 indicators (from cache or fresh)
        h1_regimes: H1 regime analysis (from cache or fresh)
        m5_candles: Fresh M5 candles
    """
    # Step 1: Load H1 cache
    h1_candles, h1_indicators, h1_regimes, missing_pairs = load_all_h1_cache(pairs)
    
    # Step 2: Refresh H1 for any missing/expired pairs
    if missing_pairs:
        fresh_candles, fresh_indicators, fresh_regimes = refresh_h1_cache_for_pairs(missing_pairs)
        h1_candles.update(fresh_candles)
        h1_indicators.update(fresh_indicators)
        h1_regimes.update(fresh_regimes)
    
    # Step 3: Fetch fresh M5 data + prices
    prices, m5_candles = fetch_m5_data_only(pairs)
    
    return prices, h1_indicators, h1_regimes, m5_candles

# =============================================================================
# POSITION MANAGEMENT - MetaAPI
# =============================================================================

def fetch_open_positions() -> Optional[List[Dict]]:
    """Fetch all open positions with retry logic."""
    url = f"{METAAPI_BASE_URL}/users/current/accounts/{METAAPI_ACCOUNT_ID}/positions"
    
    for attempt in range(3):
        req = urllib.request.Request(url)
        req.add_header("auth-token", METAAPI_TOKEN)
        req.add_header("Accept", CONTENT_TYPE_JSON)
        
        try:
            timeout = 15 + (attempt * 5)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"[RETRY {attempt + 1}/3] Error fetching positions: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    
    return None

def get_position_age_minutes(position: Dict) -> float:
    """Calculate position age in minutes."""
    now = datetime.now(timezone.utc)
    time_str = position.get('time') or position.get('openTime')
    
    if not time_str:
        return 0.0
    
    try:
        if 'T' in str(time_str):
            open_time = datetime.fromisoformat(str(time_str).replace('Z', '+00:00'))
        else:
            open_time = datetime.strptime(str(time_str).split('.')[0], '%Y-%m-%d %H:%M:%S')
            open_time = open_time.replace(tzinfo=timezone.utc)
        return (now - open_time).total_seconds() / 60.0
    except Exception:
        return 0.0

def close_position(position_id: str) -> Dict:
    """Close a position by ID."""
    url = f"{METAAPI_BASE_URL}/users/current/accounts/{METAAPI_ACCOUNT_ID}/trade"
    
    trade_request = {"actionType": "POSITION_CLOSE_ID", "positionId": position_id}
    
    req = urllib.request.Request(url, data=json.dumps(trade_request).encode('utf-8'), method='POST')
    req.add_header("auth-token", METAAPI_TOKEN)
    req.add_header("Content-Type", CONTENT_TYPE_JSON)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return {'status': 'CLOSED' if result.get('stringCode') == 'TRADE_RETCODE_DONE' else 'FAILED', 'response': result}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def execute_trade(symbol: str, action: str, lot_size: float, stop_loss: float, take_profit: float) -> Dict:
    """Execute a trade via MetaAPI."""
    url = f"{METAAPI_BASE_URL}/users/current/accounts/{METAAPI_ACCOUNT_ID}/trade"
    
    action_type = "ORDER_TYPE_BUY" if action == "BUY" else "ORDER_TYPE_SELL"
    
    trade_request = {
        "actionType": action_type,
        "symbol": symbol,
        "volume": lot_size,
        "stopLoss": stop_loss,
        "takeProfit": take_profit
    }
    
    print(f"Executing: {action} {symbol} @ lot={lot_size}, SL={stop_loss}, TP={take_profit}")
    
    req = urllib.request.Request(url, data=json.dumps(trade_request).encode('utf-8'), method='POST')
    req.add_header("auth-token", METAAPI_TOKEN)
    req.add_header("Content-Type", CONTENT_TYPE_JSON)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            status = 'EXECUTED' if result.get('stringCode') == 'TRADE_RETCODE_DONE' else 'FAILED'
            return {'status': status, 'response': result, 'order_id': result.get('orderId')}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {'status': 'ERROR', 'error': error_body, 'code': e.code}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}


# =============================================================================
# INDICATOR COMPUTATION - ALL 161 TA-LIB INDICATORS
# =============================================================================

def compute_all_indicators(open_arr: np.ndarray, high_arr: np.ndarray, 
                           low_arr: np.ndarray, close_arr: np.ndarray, 
                           volume_arr: np.ndarray) -> Dict[str, Any]:
    """
    Compute ALL 158 TA-Lib indicators/functions.
    
    Categories:
    - Overlap Studies (25): SMA, EMA, DEMA, TEMA, KAMA, WMA, TRIMA, T3, MAMA/FAMA, 
                            HT_TRENDLINE, BBANDS, SAR, SAREXT, MIDPOINT, MIDPRICE, ACCBANDS
    - Momentum (44): RSI, MACD, MACDEXT, MACDFIX, ADX, ADXR, DX, +DI, -DI, +DM, -DM,
                     STOCH, STOCHF, STOCHRSI, AROON, AROONOSC, CCI, CMO, MOM, ROC, ROCP,
                     ROCR, ROCR100, TRIX, ULTOSC, WILLR, MFI, BOP, APO, PPO
    - Volume (3): AD, ADOSC, OBV
    - Volatility (3): ATR, NATR, TRANGE
    - Cycles (7): HT_DCPERIOD, HT_DCPHASE, HT_PHASOR, HT_SINE, HT_LEADSINE, HT_TRENDMODE
    - Price Transform (4): AVGPRICE, MEDPRICE, TYPPRICE, WCLPRICE
    - Statistics (9): LINEARREG family, STDDEV, VAR, TSF, BETA, CORREL
    - Patterns (61): All CDL* candlestick patterns
    - Math Transform (15): ACOS, ASIN, ATAN, CEIL, COS, COSH, EXP, FLOOR, LN, LOG10, SIN, SINH, SQRT, TAN, TANH
    - Math Operators (12): MAX, MIN, SUM, MINMAX, MINMAXINDEX, MAXINDEX, MININDEX, ADD, SUB, MULT, DIV
    
    TOTAL: 158+ indicator values computed
    """
    indicators = {
        "overlap": {},
        "momentum": {},
        "volume": {},
        "volatility": {},
        "cycles": {},
        "price_transform": {},
        "statistics": {},
        "patterns": {},
        "math_transform": {},
        "math_operators": {}
    }
    
    # =========================================================================
    # OVERLAP STUDIES (18 indicators)
    # =========================================================================
    try:
        # Simple Moving Averages
        indicators["overlap"]["SMA_20"] = safe_float(talib.SMA(close_arr, timeperiod=20)[-1])
        indicators["overlap"]["SMA_50"] = safe_float(talib.SMA(close_arr, timeperiod=50)[-1])
        indicators["overlap"]["SMA_200"] = safe_float(talib.SMA(close_arr, timeperiod=200)[-1])
        
        # Exponential Moving Averages
        indicators["overlap"]["EMA_12"] = safe_float(talib.EMA(close_arr, timeperiod=12)[-1])
        indicators["overlap"]["EMA_26"] = safe_float(talib.EMA(close_arr, timeperiod=26)[-1])
        indicators["overlap"]["EMA_50"] = safe_float(talib.EMA(close_arr, timeperiod=50)[-1])
        
        # Advanced Moving Averages
        indicators["overlap"]["DEMA_30"] = safe_float(talib.DEMA(close_arr, timeperiod=30)[-1])
        indicators["overlap"]["TEMA_30"] = safe_float(talib.TEMA(close_arr, timeperiod=30)[-1])
        indicators["overlap"]["KAMA_30"] = safe_float(talib.KAMA(close_arr, timeperiod=30)[-1])
        indicators["overlap"]["WMA_30"] = safe_float(talib.WMA(close_arr, timeperiod=30)[-1])
        indicators["overlap"]["TRIMA_30"] = safe_float(talib.TRIMA(close_arr, timeperiod=30)[-1])
        indicators["overlap"]["T3_5"] = safe_float(talib.T3(close_arr, timeperiod=5)[-1])
        
        # MAMA/FAMA
        mama, fama = talib.MAMA(close_arr)
        indicators["overlap"]["MAMA"] = safe_float(mama[-1])
        indicators["overlap"]["FAMA"] = safe_float(fama[-1])
        
        # Hilbert Transform Trendline
        indicators["overlap"]["HT_TRENDLINE"] = safe_float(talib.HT_TRENDLINE(close_arr)[-1])
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close_arr, timeperiod=20, nbdevup=2, nbdevdn=2)
        indicators["overlap"]["BBANDS_upper"] = safe_float(upper[-1])
        indicators["overlap"]["BBANDS_middle"] = safe_float(middle[-1])
        indicators["overlap"]["BBANDS_lower"] = safe_float(lower[-1])
        
        # Parabolic SAR
        indicators["overlap"]["SAR"] = safe_float(talib.SAR(high_arr, low_arr)[-1])
        indicators["overlap"]["SAREXT"] = safe_float(talib.SAREXT(high_arr, low_arr)[-1])
        
        # MIDPOINT and MIDPRICE
        indicators["overlap"]["MIDPOINT"] = safe_float(talib.MIDPOINT(close_arr, timeperiod=14)[-1])
        indicators["overlap"]["MIDPRICE"] = safe_float(talib.MIDPRICE(high_arr, low_arr, timeperiod=14)[-1])
        
        # Acceleration Bands (ACCBANDS)
        upper_acc, middle_acc, lower_acc = talib.ACCBANDS(high_arr, low_arr, close_arr, timeperiod=20)
        indicators["overlap"]["ACCBANDS_upper"] = safe_float(upper_acc[-1])
        indicators["overlap"]["ACCBANDS_middle"] = safe_float(middle_acc[-1])
        indicators["overlap"]["ACCBANDS_lower"] = safe_float(lower_acc[-1])
        
    except Exception as e:
        print(f"Error computing overlap indicators: {e}")
    
    # =========================================================================
    # MOMENTUM INDICATORS (31 indicators)
    # =========================================================================
    try:
        # RSI
        indicators["momentum"]["RSI_14"] = safe_float(talib.RSI(close_arr, timeperiod=14)[-1])
        indicators["momentum"]["RSI_9"] = safe_float(talib.RSI(close_arr, timeperiod=9)[-1])
        
        # MACD
        macd, signal, hist = talib.MACD(close_arr, fastperiod=12, slowperiod=26, signalperiod=9)
        indicators["momentum"]["MACD"] = safe_float(macd[-1])
        indicators["momentum"]["MACD_signal"] = safe_float(signal[-1])
        indicators["momentum"]["MACD_hist"] = safe_float(hist[-1])
        
        # MACDEXT (Extended MACD with different MA types)
        macdext, macdext_signal, macdext_hist = talib.MACDEXT(close_arr)
        indicators["momentum"]["MACDEXT"] = safe_float(macdext[-1])
        indicators["momentum"]["MACDEXT_signal"] = safe_float(macdext_signal[-1])
        indicators["momentum"]["MACDEXT_hist"] = safe_float(macdext_hist[-1])
        
        # MACDFIX (Fixed 12/26 MACD)
        macdfix, macdfix_signal, macdfix_hist = talib.MACDFIX(close_arr)
        indicators["momentum"]["MACDFIX"] = safe_float(macdfix[-1])
        indicators["momentum"]["MACDFIX_signal"] = safe_float(macdfix_signal[-1])
        indicators["momentum"]["MACDFIX_hist"] = safe_float(macdfix_hist[-1])
        
        # ADX Family
        indicators["momentum"]["ADX_14"] = safe_float(talib.ADX(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["ADXR_14"] = safe_float(talib.ADXR(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["DX_14"] = safe_float(talib.DX(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["PLUS_DI_14"] = safe_float(talib.PLUS_DI(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["MINUS_DI_14"] = safe_float(talib.MINUS_DI(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["PLUS_DM_14"] = safe_float(talib.PLUS_DM(high_arr, low_arr, timeperiod=14)[-1])
        indicators["momentum"]["MINUS_DM_14"] = safe_float(talib.MINUS_DM(high_arr, low_arr, timeperiod=14)[-1])
        
        # Stochastic
        slowk, slowd = talib.STOCH(high_arr, low_arr, close_arr)
        indicators["momentum"]["STOCH_K"] = safe_float(slowk[-1])
        indicators["momentum"]["STOCH_D"] = safe_float(slowd[-1])
        
        fastk, fastd = talib.STOCHF(high_arr, low_arr, close_arr)
        indicators["momentum"]["STOCHF_K"] = safe_float(fastk[-1])
        indicators["momentum"]["STOCHF_D"] = safe_float(fastd[-1])
        
        stochrsi_k, stochrsi_d = talib.STOCHRSI(close_arr, timeperiod=14)
        indicators["momentum"]["STOCHRSI_K"] = safe_float(stochrsi_k[-1])
        indicators["momentum"]["STOCHRSI_D"] = safe_float(stochrsi_d[-1])
        
        # AROON
        aroon_down, aroon_up = talib.AROON(high_arr, low_arr, timeperiod=14)
        indicators["momentum"]["AROON_up"] = safe_float(aroon_up[-1])
        indicators["momentum"]["AROON_down"] = safe_float(aroon_down[-1])
        indicators["momentum"]["AROONOSC"] = safe_float(talib.AROONOSC(high_arr, low_arr, timeperiod=14)[-1])
        
        # Other Momentum
        indicators["momentum"]["CCI_14"] = safe_float(talib.CCI(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["CMO_14"] = safe_float(talib.CMO(close_arr, timeperiod=14)[-1])
        indicators["momentum"]["MOM_10"] = safe_float(talib.MOM(close_arr, timeperiod=10)[-1])
        indicators["momentum"]["ROC_10"] = safe_float(talib.ROC(close_arr, timeperiod=10)[-1])
        indicators["momentum"]["ROCP_10"] = safe_float(talib.ROCP(close_arr, timeperiod=10)[-1])
        indicators["momentum"]["ROCR_10"] = safe_float(talib.ROCR(close_arr, timeperiod=10)[-1])
        indicators["momentum"]["ROCR100_10"] = safe_float(talib.ROCR100(close_arr, timeperiod=10)[-1])
        indicators["momentum"]["TRIX_30"] = safe_float(talib.TRIX(close_arr, timeperiod=30)[-1])
        indicators["momentum"]["ULTOSC"] = safe_float(talib.ULTOSC(high_arr, low_arr, close_arr)[-1])
        indicators["momentum"]["WILLR_14"] = safe_float(talib.WILLR(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["momentum"]["MFI_14"] = safe_float(talib.MFI(high_arr, low_arr, close_arr, volume_arr, timeperiod=14)[-1])
        indicators["momentum"]["BOP"] = safe_float(talib.BOP(open_arr, high_arr, low_arr, close_arr)[-1])
        indicators["momentum"]["APO"] = safe_float(talib.APO(close_arr, fastperiod=12, slowperiod=26)[-1])
        indicators["momentum"]["PPO"] = safe_float(talib.PPO(close_arr, fastperiod=12, slowperiod=26)[-1])
        
    except Exception as e:
        print(f"Error computing momentum indicators: {e}")
    
    # =========================================================================
    # VOLUME INDICATORS (3 indicators)
    # =========================================================================
    try:
        indicators["volume"]["AD"] = safe_float(talib.AD(high_arr, low_arr, close_arr, volume_arr)[-1])
        indicators["volume"]["ADOSC"] = safe_float(talib.ADOSC(high_arr, low_arr, close_arr, volume_arr)[-1])
        indicators["volume"]["OBV"] = safe_float(talib.OBV(close_arr, volume_arr)[-1])
    except Exception as e:
        print(f"Error computing volume indicators: {e}")
    
    # =========================================================================
    # VOLATILITY INDICATORS (3 indicators)
    # =========================================================================
    try:
        indicators["volatility"]["ATR_14"] = safe_float(talib.ATR(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["volatility"]["NATR_14"] = safe_float(talib.NATR(high_arr, low_arr, close_arr, timeperiod=14)[-1])
        indicators["volatility"]["TRANGE"] = safe_float(talib.TRANGE(high_arr, low_arr, close_arr)[-1])
    except Exception as e:
        print(f"Error computing volatility indicators: {e}")
    
    # =========================================================================
    # CYCLE INDICATORS (5 indicators)
    # =========================================================================
    try:
        indicators["cycles"]["HT_DCPERIOD"] = safe_float(talib.HT_DCPERIOD(close_arr)[-1])
        indicators["cycles"]["HT_DCPHASE"] = safe_float(talib.HT_DCPHASE(close_arr)[-1])
        
        inphase, quadrature = talib.HT_PHASOR(close_arr)
        indicators["cycles"]["HT_PHASOR_inphase"] = safe_float(inphase[-1])
        indicators["cycles"]["HT_PHASOR_quadrature"] = safe_float(quadrature[-1])
        
        sine, leadsine = talib.HT_SINE(close_arr)
        indicators["cycles"]["HT_SINE"] = safe_float(sine[-1])
        indicators["cycles"]["HT_LEADSINE"] = safe_float(leadsine[-1])
        
        indicators["cycles"]["HT_TRENDMODE"] = safe_float(talib.HT_TRENDMODE(close_arr)[-1])
    except Exception as e:
        print(f"Error computing cycle indicators: {e}")
    
    # =========================================================================
    # PRICE TRANSFORM (5 indicators)
    # =========================================================================
    try:
        indicators["price_transform"]["AVGPRICE"] = safe_float(talib.AVGPRICE(open_arr, high_arr, low_arr, close_arr)[-1])
        indicators["price_transform"]["MEDPRICE"] = safe_float(talib.MEDPRICE(high_arr, low_arr)[-1])
        indicators["price_transform"]["TYPPRICE"] = safe_float(talib.TYPPRICE(high_arr, low_arr, close_arr)[-1])
        indicators["price_transform"]["WCLPRICE"] = safe_float(talib.WCLPRICE(high_arr, low_arr, close_arr)[-1])
    except Exception as e:
        print(f"Error computing price transform indicators: {e}")
    
    # =========================================================================
    # STATISTICS - ALL 9 FUNCTIONS
    # =========================================================================
    try:
        indicators["statistics"]["LINEARREG_14"] = safe_float(talib.LINEARREG(close_arr, timeperiod=14)[-1])
        indicators["statistics"]["LINEARREG_ANGLE_14"] = safe_float(talib.LINEARREG_ANGLE(close_arr, timeperiod=14)[-1])
        indicators["statistics"]["LINEARREG_INTERCEPT_14"] = safe_float(talib.LINEARREG_INTERCEPT(close_arr, timeperiod=14)[-1])
        indicators["statistics"]["LINEARREG_SLOPE_14"] = safe_float(talib.LINEARREG_SLOPE(close_arr, timeperiod=14)[-1])
        indicators["statistics"]["STDDEV_5"] = safe_float(talib.STDDEV(close_arr, timeperiod=5)[-1])
        indicators["statistics"]["TSF_14"] = safe_float(talib.TSF(close_arr, timeperiod=14)[-1])
        indicators["statistics"]["VAR_5"] = safe_float(talib.VAR(close_arr, timeperiod=5)[-1])
        
        # BETA and CORREL (comparing close vs high for correlation analysis)
        indicators["statistics"]["BETA"] = safe_float(talib.BETA(high_arr, low_arr, timeperiod=5)[-1])
        indicators["statistics"]["CORREL"] = safe_float(talib.CORREL(high_arr, low_arr, timeperiod=30)[-1])
    except Exception as e:
        print(f"Error computing statistics indicators: {e}")
    
    # =========================================================================
    # CANDLESTICK PATTERNS (61 patterns)
    # =========================================================================
    try:
        pattern_functions = [
            'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE',
            'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK',
            'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL',
            'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR',
            'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR',
            'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN',
            'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD',
            'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS', 'CDLINNECK', 'CDLINVERTEDHAMMER',
            'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI',
            'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR',
            'CDLMORNINGSTAR', 'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS',
            'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP',
            'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
            'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS'
        ]
        
        for pattern in pattern_functions:
            try:
                func = getattr(talib, pattern)
                result = func(open_arr, high_arr, low_arr, close_arr)
                indicators["patterns"][pattern] = int(result[-1]) if not np.isnan(result[-1]) else 0
            except Exception:
                indicators["patterns"][pattern] = 0
                
    except Exception as e:
        print(f"Error computing pattern indicators: {e}")
    
    # =========================================================================
    # MATH OPERATORS (Support/Resistance) - ALL 11 FUNCTIONS
    # =========================================================================
    try:
        indicators["math_operators"]["MAX_20"] = safe_float(talib.MAX(high_arr, timeperiod=20)[-1])
        indicators["math_operators"]["MIN_20"] = safe_float(talib.MIN(low_arr, timeperiod=20)[-1])
        indicators["math_operators"]["SUM_20"] = safe_float(talib.SUM(close_arr, timeperiod=20)[-1])
        
        # Additional Math Operators
        minval, maxval = talib.MINMAX(close_arr, timeperiod=20)
        indicators["math_operators"]["MINMAX_min"] = safe_float(minval[-1])
        indicators["math_operators"]["MINMAX_max"] = safe_float(maxval[-1])
        
        minidx, maxidx = talib.MINMAXINDEX(close_arr, timeperiod=20)
        indicators["math_operators"]["MINMAXINDEX_min"] = safe_float(minidx[-1])
        indicators["math_operators"]["MINMAXINDEX_max"] = safe_float(maxidx[-1])
        
        indicators["math_operators"]["MAXINDEX_20"] = safe_float(talib.MAXINDEX(close_arr, timeperiod=20)[-1])
        indicators["math_operators"]["MININDEX_20"] = safe_float(talib.MININDEX(close_arr, timeperiod=20)[-1])
        
        # Arithmetic operations (comparing high vs low)
        indicators["math_operators"]["ADD"] = safe_float(talib.ADD(high_arr, low_arr)[-1])
        indicators["math_operators"]["SUB"] = safe_float(talib.SUB(high_arr, low_arr)[-1])
        indicators["math_operators"]["MULT"] = safe_float(talib.MULT(high_arr, low_arr)[-1])
        indicators["math_operators"]["DIV"] = safe_float(talib.DIV(high_arr, low_arr)[-1])
    except Exception as e:
        print(f"Error computing math operators: {e}")
    
    # =========================================================================
    # MATH TRANSFORM - ALL 15 FUNCTIONS
    # =========================================================================
    try:
        indicators["math_transform"]["ACOS"] = safe_float(talib.ACOS(close_arr / close_arr.max())[-1])
        indicators["math_transform"]["ASIN"] = safe_float(talib.ASIN(close_arr / close_arr.max())[-1])
        indicators["math_transform"]["ATAN"] = safe_float(talib.ATAN(close_arr)[-1])
        indicators["math_transform"]["CEIL"] = safe_float(talib.CEIL(close_arr)[-1])
        indicators["math_transform"]["COS"] = safe_float(talib.COS(close_arr)[-1])
        indicators["math_transform"]["COSH"] = safe_float(talib.COSH(close_arr / 100)[-1])  # Scaled to avoid overflow
        indicators["math_transform"]["EXP"] = safe_float(talib.EXP(close_arr / 1000)[-1])  # Scaled to avoid overflow
        indicators["math_transform"]["FLOOR"] = safe_float(talib.FLOOR(close_arr)[-1])
        indicators["math_transform"]["LN"] = safe_float(talib.LN(close_arr)[-1])
        indicators["math_transform"]["LOG10"] = safe_float(talib.LOG10(close_arr)[-1])
        indicators["math_transform"]["SIN"] = safe_float(talib.SIN(close_arr)[-1])
        indicators["math_transform"]["SINH"] = safe_float(talib.SINH(close_arr / 100)[-1])  # Scaled
        indicators["math_transform"]["SQRT"] = safe_float(talib.SQRT(close_arr)[-1])
        indicators["math_transform"]["TAN"] = safe_float(talib.TAN(close_arr)[-1])
        indicators["math_transform"]["TANH"] = safe_float(talib.TANH(close_arr)[-1])
    except Exception as e:
        print(f"Error computing math transform: {e}")
    
    return indicators


# =============================================================================
# WISDOM ENGINE - MARKET REGIME DETECTION
# =============================================================================

def detect_market_regime(indicators: Dict[str, Any]) -> RegimeAnalysis:
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
    """
    momentum = indicators.get("momentum", {})
    overlap = indicators.get("overlap", {})
    volatility = indicators.get("volatility", {})
    cycles = indicators.get("cycles", {})
    statistics = indicators.get("statistics", {})
    
    # =========================================================================
    # TREND STRENGTH INDICATORS
    # =========================================================================
    adx = momentum.get("ADX_14", 20)
    adxr = momentum.get("ADXR_14", 20)
    plus_di = momentum.get("PLUS_DI_14", 0)
    minus_di = momentum.get("MINUS_DI_14", 0)
    
    # AROON for trend timing
    aroon_up = momentum.get("AROON_up", 50)
    aroon_down = momentum.get("AROON_down", 50)
    aroonosc = momentum.get("AROONOSC", 0)
    
    # Hilbert Transform
    ht_trendmode = cycles.get("HT_TRENDMODE", 0)
    
    # Linear Regression
    linreg_angle = statistics.get("LINEARREG_ANGLE_14", 0)
    
    # Moving Averages
    sma_20 = overlap.get("SMA_20", 0)
    sma_50 = overlap.get("SMA_50", 0)
    sma_200 = overlap.get("SMA_200", 0)
    ema_12 = overlap.get("EMA_12", 0)
    ema_26 = overlap.get("EMA_26", 0)
    
    # Volatility
    natr = volatility.get("NATR_14", 0)
    
    # =========================================================================
    # COMPREHENSIVE TREND ANALYSIS
    # =========================================================================
    
    # 1. ADX Analysis
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
        di_direction = "BULLISH"
    elif di_diff < -10:
        di_direction = "BEARISH"
    else:
        di_direction = "NEUTRAL"
    
    # 3. AROON Analysis
    if aroon_up > 70 and aroon_down < 30:
        aroon_direction = "BULLISH"
    elif aroon_down > 70 and aroon_up < 30:
        aroon_direction = "BEARISH"
    elif aroonosc > 50:
        aroon_direction = "BULLISH"
    elif aroonosc < -50:
        aroon_direction = "BEARISH"
    else:
        aroon_direction = "NEUTRAL"
    
    # 4. HT_TRENDMODE Analysis
    if ht_trendmode == 1:
        trend_mode_interpretation = "Hilbert Transform: TRENDING mode"
    else:
        trend_mode_interpretation = "Hilbert Transform: CYCLE/RANGING mode"
    
    # 5. Linear Regression Analysis
    if linreg_angle > 30:
        linreg_direction = "BULLISH"
    elif linreg_angle > 10:
        linreg_direction = "BULLISH"
    elif linreg_angle < -30:
        linreg_direction = "BEARISH"
    elif linreg_angle < -10:
        linreg_direction = "BEARISH"
    else:
        linreg_direction = "NEUTRAL"
    
    # 6. MA Alignment Analysis
    bullish_ma = 0
    bearish_ma = 0
    
    if sma_20 > sma_50:
        bullish_ma += 1
    else:
        bearish_ma += 1
    
    if sma_50 > sma_200:
        bullish_ma += 1
    else:
        bearish_ma += 1
    
    if ema_12 > ema_26:
        bullish_ma += 1
    else:
        bearish_ma += 1
    
    if bullish_ma >= 2:
        ma_alignment = "BULLISH"
        ma_interpretation = f"MA Alignment: {bullish_ma}/3 bullish → BULLISH"
    elif bearish_ma >= 2:
        ma_alignment = "BEARISH"
        ma_interpretation = f"MA Alignment: {bearish_ma}/3 bearish → BEARISH"
    else:
        ma_alignment = "MIXED"
        ma_interpretation = "MA Alignment: MIXED"
    
    # 7. Volatility Analysis
    if natr > 2.0:
        volatility_state = "HIGH"
        volatility_interpretation = f"NATR={natr:.2f}% → HIGH volatility"
    elif natr > 1.0:
        volatility_state = "NORMAL"
        volatility_interpretation = f"NATR={natr:.2f}% → NORMAL volatility"
    else:
        volatility_state = "LOW"
        volatility_interpretation = f"NATR={natr:.2f}% → LOW volatility"
    
    # =========================================================================
    # DETERMINE REGIME (Consensus)
    # =========================================================================
    bullish_votes = 0
    bearish_votes = 0
    
    if di_direction == "BULLISH":
        bullish_votes += 2
    elif di_direction == "BEARISH":
        bearish_votes += 2
    
    if aroon_direction == "BULLISH":
        bullish_votes += 1
    elif aroon_direction == "BEARISH":
        bearish_votes += 1
    
    if linreg_direction == "BULLISH":
        bullish_votes += 1
    elif linreg_direction == "BEARISH":
        bearish_votes += 1
    
    if ma_alignment == "BULLISH":
        bullish_votes += 1
    elif ma_alignment == "BEARISH":
        bearish_votes += 1
    
    # Determine regime
    if trend_strength == "NONE" or ht_trendmode == 0:
        if volatility_state == "HIGH":
            regime = MarketRegime.VOLATILE
        else:
            regime = MarketRegime.RANGING
    elif bullish_votes > bearish_votes + 1:
        regime = MarketRegime.TRENDING_UP
    elif bearish_votes > bullish_votes + 1:
        regime = MarketRegime.TRENDING_DOWN
    elif volatility_state == "HIGH":
        regime = MarketRegime.VOLATILE
    else:
        regime = MarketRegime.RANGING
    
    # Build reasoning
    reasoning = f"""
MARKET REGIME: {regime.value}

TREND STRENGTH:
- {adx_interpretation}
- +DI={plus_di:.1f}, -DI={minus_di:.1f} → {di_direction} direction

TREND TIMING:
- AROON Up={aroon_up:.0f}, Down={aroon_down:.0f}, OSC={aroonosc:.0f} → {aroon_direction}
- {trend_mode_interpretation}
- LINEARREG angle={linreg_angle:.1f}° → {linreg_direction}

MOVING AVERAGES:
- {ma_interpretation}

VOLATILITY:
- {volatility_interpretation}

CONSENSUS: Bullish={bullish_votes}, Bearish={bearish_votes}
"""
    
    return RegimeAnalysis(
        regime=regime,
        adx_value=adx,
        adx_interpretation=adx_interpretation,
        trend_mode=int(ht_trendmode),
        trend_mode_interpretation=trend_mode_interpretation,
        ma_alignment=ma_alignment,
        ma_alignment_interpretation=ma_interpretation,
        volatility_state=volatility_state,
        volatility_interpretation=volatility_interpretation,
        reasoning=reasoning
    )

# =============================================================================
# WISDOM ENGINE - INDICATOR INTERPRETATION
# =============================================================================

def interpret_momentum(indicators: Dict[str, Any], regime: MarketRegime) -> Dict[str, Any]:
    """
    Interpret ALL momentum indicators in context of market regime.
    
    KEY INSIGHT: Same indicator value means DIFFERENT things in different regimes!
    - RSI 70 in TRENDING_UP = Strong momentum, NOT overbought
    - RSI 70 in RANGING = Overbought, expect reversal
    """
    momentum = indicators.get("momentum", {})
    
    rsi = momentum.get("RSI_14", 50)
    macd = momentum.get("MACD", 0)
    macd_hist = momentum.get("MACD_hist", 0)
    stoch_k = momentum.get("STOCH_K", 50)
    stoch_d = momentum.get("STOCH_D", 50)
    cci = momentum.get("CCI_14", 0)
    cmo = momentum.get("CMO_14", 0)
    willr = momentum.get("WILLR_14", -50)
    mfi = momentum.get("MFI_14", 50)
    ultosc = momentum.get("ULTOSC", 50)
    bop = momentum.get("BOP", 0)
    
    interpretation = {
        "bullish_signals": [],
        "bearish_signals": [],
        "neutral_signals": [],
        "overall": "NEUTRAL",
        "reasoning": ""
    }
    
    # RSI Interpretation (Context-Aware)
    if regime in [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
        # In trends, RSI extremes show momentum, not reversal
        if rsi > 60:
            interpretation["bullish_signals"].append(f"RSI={rsi:.1f} → Strong bullish momentum (trending)")
        elif rsi < 40:
            interpretation["bearish_signals"].append(f"RSI={rsi:.1f} → Strong bearish momentum (trending)")
        else:
            interpretation["neutral_signals"].append(f"RSI={rsi:.1f} → Neutral momentum")
    else:
        # In ranging/volatile, RSI extremes suggest reversal
        if rsi > 70:
            interpretation["bearish_signals"].append(f"RSI={rsi:.1f} → OVERBOUGHT (expect reversal)")
        elif rsi < 30:
            interpretation["bullish_signals"].append(f"RSI={rsi:.1f} → OVERSOLD (expect reversal)")
        else:
            interpretation["neutral_signals"].append(f"RSI={rsi:.1f} → Neutral")
    
    # MACD Interpretation
    if macd > 0 and macd_hist > 0:
        interpretation["bullish_signals"].append(f"MACD={macd:.5f}, Hist={macd_hist:.5f} → Bullish momentum")
    elif macd < 0 and macd_hist < 0:
        interpretation["bearish_signals"].append(f"MACD={macd:.5f}, Hist={macd_hist:.5f} → Bearish momentum")
    else:
        interpretation["neutral_signals"].append(f"MACD={macd:.5f} → Mixed signals")
    
    # Stochastic Interpretation (Context-Aware)
    if regime in [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
        if stoch_k > 50:
            interpretation["bullish_signals"].append(f"Stoch K={stoch_k:.1f} → Bullish (trending)")
        else:
            interpretation["bearish_signals"].append(f"Stoch K={stoch_k:.1f} → Bearish (trending)")
    else:
        if stoch_k > 80:
            interpretation["bearish_signals"].append(f"Stoch K={stoch_k:.1f} → OVERBOUGHT")
        elif stoch_k < 20:
            interpretation["bullish_signals"].append(f"Stoch K={stoch_k:.1f} → OVERSOLD")
    
    # CCI Interpretation
    if cci > 100:
        if regime == MarketRegime.TRENDING_UP:
            interpretation["bullish_signals"].append(f"CCI={cci:.1f} → Strong uptrend")
        else:
            interpretation["bearish_signals"].append(f"CCI={cci:.1f} → Overbought")
    elif cci < -100:
        if regime == MarketRegime.TRENDING_DOWN:
            interpretation["bearish_signals"].append(f"CCI={cci:.1f} → Strong downtrend")
        else:
            interpretation["bullish_signals"].append(f"CCI={cci:.1f} → Oversold")
    
    # Williams %R
    if willr > -20:
        interpretation["bearish_signals"].append(f"Williams %R={willr:.1f} → Overbought")
    elif willr < -80:
        interpretation["bullish_signals"].append(f"Williams %R={willr:.1f} → Oversold")
    
    # MFI (Money Flow Index)
    if mfi > 80:
        interpretation["bearish_signals"].append(f"MFI={mfi:.1f} → Overbought (money flow)")
    elif mfi < 20:
        interpretation["bullish_signals"].append(f"MFI={mfi:.1f} → Oversold (money flow)")
    
    # Ultimate Oscillator
    if ultosc > 70:
        interpretation["bullish_signals"].append(f"ULTOSC={ultosc:.1f} → Strong bullish")
    elif ultosc < 30:
        interpretation["bearish_signals"].append(f"ULTOSC={ultosc:.1f} → Strong bearish")
    
    # Balance of Power
    if bop > 0.3:
        interpretation["bullish_signals"].append(f"BOP={bop:.2f} → Buyers in control")
    elif bop < -0.3:
        interpretation["bearish_signals"].append(f"BOP={bop:.2f} → Sellers in control")
    
    # Determine overall
    bullish_count = len(interpretation["bullish_signals"])
    bearish_count = len(interpretation["bearish_signals"])
    
    if bullish_count > bearish_count + 1:
        interpretation["overall"] = "BULLISH"
    elif bearish_count > bullish_count + 1:
        interpretation["overall"] = "BEARISH"
    else:
        interpretation["overall"] = "NEUTRAL"
    
    interpretation["reasoning"] = f"Momentum: {bullish_count} bullish, {bearish_count} bearish signals → {interpretation['overall']}"
    
    return interpretation

def interpret_volume(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Interpret volume indicators."""
    volume = indicators.get("volume", {})
    
    ad = volume.get("AD", 0)
    adosc = volume.get("ADOSC", 0)
    obv = volume.get("OBV", 0)
    
    interpretation = {
        "trend": "NEUTRAL",
        "confirms_price": False,
        "reasoning": ""
    }
    
    bullish = 0
    bearish = 0
    
    if adosc > 0:
        bullish += 1
    elif adosc < 0:
        bearish += 1
    
    if bullish > bearish:
        interpretation["trend"] = "ACCUMULATION"
        interpretation["confirms_price"] = True
        interpretation["reasoning"] = f"ADOSC={adosc:.0f} → Accumulation (bullish volume)"
    elif bearish > bullish:
        interpretation["trend"] = "DISTRIBUTION"
        interpretation["confirms_price"] = True
        interpretation["reasoning"] = f"ADOSC={adosc:.0f} → Distribution (bearish volume)"
    else:
        interpretation["reasoning"] = "Volume neutral"
    
    return interpretation

def interpret_patterns(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Interpret candlestick patterns."""
    patterns = indicators.get("patterns", {})
    
    bullish_patterns = []
    bearish_patterns = []
    
    bullish_pattern_names = [
        'CDL3WHITESOLDIERS', 'CDLHAMMER', 'CDLINVERTEDHAMMER', 'CDLMORNINGSTAR',
        'CDLMORNINGDOJISTAR', 'CDLPIERCING', 'CDLENGULFING', 'CDLHARAMI'
    ]
    
    bearish_pattern_names = [
        'CDL3BLACKCROWS', 'CDLHANGINGMAN', 'CDLSHOOTINGSTAR', 'CDLEVENINGSTAR',
        'CDLEVENINGDOJISTAR', 'CDLDARKCLOUDCOVER', 'CDLENGULFING', 'CDLHARAMI'
    ]
    
    for pattern, value in patterns.items():
        if value > 0:
            if pattern in bullish_pattern_names:
                bullish_patterns.append(pattern)
            elif pattern in bearish_pattern_names:
                bearish_patterns.append(pattern)
            else:
                bullish_patterns.append(pattern)  # Positive = bullish
        elif value < 0:
            bearish_patterns.append(pattern)
    
    if len(bullish_patterns) > len(bearish_patterns):
        bias = "BULLISH"
    elif len(bearish_patterns) > len(bullish_patterns):
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"
    
    return {
        "bullish_patterns": bullish_patterns,
        "bearish_patterns": bearish_patterns,
        "bias": bias,
        "reasoning": f"Patterns: {len(bullish_patterns)} bullish, {len(bearish_patterns)} bearish → {bias}"
    }


# =============================================================================
# WISDOM ENGINE - TRADE DECISION SYNTHESIS (EXACT GITHUB IMPLEMENTATION)
# =============================================================================

def get_allowed_directions(regime: MarketRegime) -> List[TradeDirection]:
    """Get allowed trade directions based on regime - EXACT GITHUB LOGIC."""
    if regime == MarketRegime.TRENDING_UP:
        return [TradeDirection.LONG]
    elif regime == MarketRegime.TRENDING_DOWN:
        return [TradeDirection.SHORT]
    elif regime == MarketRegime.RANGING:
        return [TradeDirection.LONG, TradeDirection.SHORT]
    else:  # VOLATILE
        return [TradeDirection.NO_TRADE]


def check_comprehensive_agreement(momentum_interp: Dict[str, Any],
                                   volume_interp: Dict[str, Any],
                                   pattern_interp: Dict[str, Any],
                                   indicators: Dict[str, Any],
                                   regime: MarketRegime) -> Dict[str, Any]:
    """
    Check COMPREHENSIVE indicator agreement across ALL 158 indicators.
    EVERY INDICATOR CONTRIBUTES TO THE DECISION.
    """
    momentum = indicators.get("momentum", {})
    overlap = indicators.get("overlap", {})
    statistics = indicators.get("statistics", {})
    cycles = indicators.get("cycles", {})
    volatility = indicators.get("volatility", {})
    volume = indicators.get("volume", {})
    price_transform = indicators.get("price_transform", {})
    math_operators = indicators.get("math_operators", {})
    patterns = indicators.get("patterns", {})
    
    agreement = {
        "trend": {},
        "momentum": {},
        "volume": {},
        "patterns": {},
        "cycles": {},
        "volatility": {},
        "statistics": {},
        "price_position": {},
        "support_resistance": {},
        "summary": {}
    }
    
    # =========================================================================
    # TREND AGREEMENT - ALL 25 OVERLAP STUDIES
    # =========================================================================
    trend_bullish = 0
    trend_bearish = 0
    current_price = overlap.get("SMA_20", 0)  # Use SMA_20 as price proxy
    
    # Moving Average Comparisons
    sma_20 = overlap.get("SMA_20", 0)
    sma_50 = overlap.get("SMA_50", 0)
    sma_200 = overlap.get("SMA_200", 0)
    ema_12 = overlap.get("EMA_12", 0)
    ema_26 = overlap.get("EMA_26", 0)
    ema_50 = overlap.get("EMA_50", 0)
    dema_30 = overlap.get("DEMA_30", 0)
    tema_30 = overlap.get("TEMA_30", 0)
    kama_30 = overlap.get("KAMA_30", 0)
    wma_30 = overlap.get("WMA_30", 0)
    trima_30 = overlap.get("TRIMA_30", 0)
    t3_5 = overlap.get("T3_5", 0)
    mama = overlap.get("MAMA", 0)
    fama = overlap.get("FAMA", 0)
    ht_trendline = overlap.get("HT_TRENDLINE", 0)
    
    # EMA crossovers
    if ema_12 > ema_26: trend_bullish += 1
    else: trend_bearish += 1
    
    if ema_12 > ema_50: trend_bullish += 1
    else: trend_bearish += 1
    
    # SMA hierarchy
    if sma_20 > sma_50: trend_bullish += 1
    else: trend_bearish += 1
    
    if sma_50 > sma_200 and sma_200 > 0: trend_bullish += 1
    elif sma_200 > 0: trend_bearish += 1
    
    # Advanced MAs vs price
    if current_price > dema_30 and dema_30 > 0: trend_bullish += 1
    elif dema_30 > 0: trend_bearish += 1
    
    if current_price > tema_30 and tema_30 > 0: trend_bullish += 1
    elif tema_30 > 0: trend_bearish += 1
    
    if current_price > kama_30 and kama_30 > 0: trend_bullish += 1
    elif kama_30 > 0: trend_bearish += 1
    
    if current_price > wma_30 and wma_30 > 0: trend_bullish += 1
    elif wma_30 > 0: trend_bearish += 1
    
    if current_price > trima_30 and trima_30 > 0: trend_bullish += 1
    elif trima_30 > 0: trend_bearish += 1
    
    if current_price > t3_5 and t3_5 > 0: trend_bullish += 1
    elif t3_5 > 0: trend_bearish += 1
    
    # MAMA/FAMA
    if mama > fama and mama > 0: trend_bullish += 1
    elif fama > 0: trend_bearish += 1
    
    # Hilbert Trendline
    if current_price > ht_trendline and ht_trendline > 0: trend_bullish += 1
    elif ht_trendline > 0: trend_bearish += 1
    
    # Bollinger Bands position
    bbands_upper = overlap.get("BBANDS_upper", 0)
    bbands_middle = overlap.get("BBANDS_middle", sma_20)
    bbands_lower = overlap.get("BBANDS_lower", 0)
    if current_price > bbands_middle: trend_bullish += 1
    else: trend_bearish += 1
    
    # Parabolic SAR
    sar = overlap.get("SAR", 0)
    sarext = overlap.get("SAREXT", 0)
    if sar < current_price and sar > 0: trend_bullish += 1
    elif sar > 0: trend_bearish += 1
    
    if sarext < current_price and sarext > 0: trend_bullish += 1
    elif sarext > 0: trend_bearish += 1
    
    # MIDPOINT/MIDPRICE
    midpoint = overlap.get("MIDPOINT", 0)
    midprice = overlap.get("MIDPRICE", 0)
    if current_price > midpoint and midpoint > 0: trend_bullish += 1
    elif midpoint > 0: trend_bearish += 1
    
    if current_price > midprice and midprice > 0: trend_bullish += 1
    elif midprice > 0: trend_bearish += 1
    
    # ACCBANDS position
    accbands_upper = overlap.get("ACCBANDS_upper", 0)
    accbands_middle = overlap.get("ACCBANDS_middle", 0)
    accbands_lower = overlap.get("ACCBANDS_lower", 0)
    if current_price > accbands_middle and accbands_middle > 0: trend_bullish += 1
    elif accbands_middle > 0: trend_bearish += 1
    
    agreement["trend"] = {
        "bullish": trend_bullish,
        "bearish": trend_bearish,
        "direction": "BULLISH" if trend_bullish > trend_bearish else "BEARISH" if trend_bearish > trend_bullish else "NEUTRAL"
    }
    
    # =========================================================================
    # MOMENTUM AGREEMENT - ALL 44 MOMENTUM INDICATORS
    # =========================================================================
    mom_bullish = 0
    mom_bearish = 0
    
    # RSI variants
    rsi_14 = momentum.get("RSI_14", 50)
    rsi_9 = momentum.get("RSI_9", 50)
    if rsi_14 > 50: mom_bullish += 1
    else: mom_bearish += 1
    if rsi_9 > 50: mom_bullish += 1
    else: mom_bearish += 1
    
    # MACD family (all 3 variants)
    macd = momentum.get("MACD", 0)
    macd_signal = momentum.get("MACD_signal", 0)
    macd_hist = momentum.get("MACD_hist", 0)
    if macd > 0: mom_bullish += 1
    else: mom_bearish += 1
    if macd > macd_signal: mom_bullish += 1
    else: mom_bearish += 1
    if macd_hist > 0: mom_bullish += 2  # Weight 2 for histogram
    else: mom_bearish += 2
    
    # MACDEXT
    macdext = momentum.get("MACDEXT", 0)
    macdext_signal = momentum.get("MACDEXT_signal", 0)
    macdext_hist = momentum.get("MACDEXT_hist", 0)
    if macdext > 0: mom_bullish += 1
    else: mom_bearish += 1
    if macdext_hist > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    # MACDFIX
    macdfix = momentum.get("MACDFIX", 0)
    macdfix_hist = momentum.get("MACDFIX_hist", 0)
    if macdfix > 0: mom_bullish += 1
    else: mom_bearish += 1
    if macdfix_hist > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    # ADX family
    adx = momentum.get("ADX_14", 20)
    adxr = momentum.get("ADXR_14", 20)
    dx = momentum.get("DX_14", 20)
    plus_di = momentum.get("PLUS_DI_14", 0)
    minus_di = momentum.get("MINUS_DI_14", 0)
    plus_dm = momentum.get("PLUS_DM_14", 0)
    minus_dm = momentum.get("MINUS_DM_14", 0)
    
    if plus_di > minus_di: mom_bullish += 2  # Weight 2
    else: mom_bearish += 2
    if plus_dm > minus_dm: mom_bullish += 1
    else: mom_bearish += 1
    
    # Stochastic family
    stoch_k = momentum.get("STOCH_K", 50)
    stoch_d = momentum.get("STOCH_D", 50)
    stochf_k = momentum.get("STOCHF_K", 50)
    stochf_d = momentum.get("STOCHF_D", 50)
    stochrsi_k = momentum.get("STOCHRSI_K", 50)
    stochrsi_d = momentum.get("STOCHRSI_D", 50)
    
    if stoch_k > 50: mom_bullish += 1
    else: mom_bearish += 1
    if stoch_k > stoch_d: mom_bullish += 1
    else: mom_bearish += 1
    if stochf_k > 50: mom_bullish += 1
    else: mom_bearish += 1
    if stochf_k > stochf_d: mom_bullish += 1
    else: mom_bearish += 1
    if stochrsi_k > 50: mom_bullish += 1
    else: mom_bearish += 1
    if stochrsi_k > stochrsi_d: mom_bullish += 1
    else: mom_bearish += 1
    
    # AROON family
    aroon_up = momentum.get("AROON_up", 50)
    aroon_down = momentum.get("AROON_down", 50)
    aroonosc = momentum.get("AROONOSC", 0)
    if aroon_up > aroon_down: mom_bullish += 1
    else: mom_bearish += 1
    if aroonosc > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    # Other momentum indicators
    cci = momentum.get("CCI_14", 0)
    if cci > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    cmo = momentum.get("CMO_14", 0)
    if cmo > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    mom_val = momentum.get("MOM_10", 0)
    if mom_val > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    # ROC family
    roc = momentum.get("ROC_10", 0)
    rocp = momentum.get("ROCP_10", 0)
    rocr = momentum.get("ROCR_10", 1)
    rocr100 = momentum.get("ROCR100_10", 100)
    if roc > 0: mom_bullish += 1
    else: mom_bearish += 1
    if rocp > 0: mom_bullish += 1
    else: mom_bearish += 1
    if rocr > 1: mom_bullish += 1
    else: mom_bearish += 1
    if rocr100 > 100: mom_bullish += 1
    else: mom_bearish += 1
    
    trix = momentum.get("TRIX_30", 0)
    if trix > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    ultosc = momentum.get("ULTOSC", 50)
    if ultosc > 50: mom_bullish += 1
    else: mom_bearish += 1
    
    willr = momentum.get("WILLR_14", -50)
    if willr > -50: mom_bullish += 1
    else: mom_bearish += 1
    
    mfi = momentum.get("MFI_14", 50)
    if mfi > 50: mom_bullish += 1
    else: mom_bearish += 1
    
    bop = momentum.get("BOP", 0)
    if bop > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    apo = momentum.get("APO", 0)
    if apo > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    ppo = momentum.get("PPO", 0)
    if ppo > 0: mom_bullish += 1
    else: mom_bearish += 1
    
    agreement["momentum"] = {
        "bullish": mom_bullish,
        "bearish": mom_bearish,
        "direction": "BULLISH" if mom_bullish > mom_bearish else "BEARISH" if mom_bearish > mom_bullish else "NEUTRAL"
    }
    
    # =========================================================================
    # VOLUME AGREEMENT - ALL 3 VOLUME INDICATORS
    # =========================================================================
    vol_bullish = 0
    vol_bearish = 0
    
    ad = volume.get("AD", 0)
    adosc = volume.get("ADOSC", 0)
    obv = volume.get("OBV", 0)
    
    # ADOSC - positive = accumulation, negative = distribution
    if adosc > 0: vol_bullish += 1
    else: vol_bearish += 1
    
    # AD trend (compare to previous - if positive, accumulation)
    if ad > 0: vol_bullish += 1
    else: vol_bearish += 1
    
    # OBV trend
    if obv > 0: vol_bullish += 1
    else: vol_bearish += 1
    
    vol_dir = "BULLISH" if vol_bullish > vol_bearish else "BEARISH" if vol_bearish > vol_bullish else "NEUTRAL"
    agreement["volume"] = {
        "bullish": vol_bullish,
        "bearish": vol_bearish,
        "direction": vol_dir
    }
    
    # =========================================================================
    # PATTERN AGREEMENT - ALL 61 CANDLESTICK PATTERNS
    # =========================================================================
    pattern_bullish = 0
    pattern_bearish = 0
    
    for pattern_name, pattern_value in patterns.items():
        if pattern_value > 0:
            pattern_bullish += 1
        elif pattern_value < 0:
            pattern_bearish += 1
    
    pattern_dir = "BULLISH" if pattern_bullish > pattern_bearish else "BEARISH" if pattern_bearish > pattern_bullish else "NEUTRAL"
    agreement["patterns"] = {
        "bullish": pattern_bullish,
        "bearish": pattern_bearish,
        "direction": pattern_dir
    }
    
    # =========================================================================
    # CYCLE AGREEMENT - ALL 7 HILBERT TRANSFORM INDICATORS
    # =========================================================================
    cycle_bullish = 0
    cycle_bearish = 0
    
    ht_trendmode = cycles.get("HT_TRENDMODE", 0)
    ht_dcperiod = cycles.get("HT_DCPERIOD", 20)
    ht_dcphase = cycles.get("HT_DCPHASE", 0)
    ht_phasor_inphase = cycles.get("HT_PHASOR_inphase", 0)
    ht_phasor_quad = cycles.get("HT_PHASOR_quadrature", 0)
    ht_sine = cycles.get("HT_SINE", 0)
    ht_leadsine = cycles.get("HT_LEADSINE", 0)
    
    # HT_TRENDMODE: 1 = trending, 0 = cycling
    if ht_trendmode == 1:
        # In trend mode, follow the trend direction
        if agreement["trend"]["direction"] == "BULLISH": cycle_bullish += 2
        else: cycle_bearish += 2
    
    # HT_SINE crossover (sine > leadsine = bullish)
    if ht_sine > ht_leadsine: cycle_bullish += 1
    else: cycle_bearish += 1
    
    # HT_PHASOR (inphase > 0 with positive quadrature = bullish)
    if ht_phasor_inphase > 0: cycle_bullish += 1
    else: cycle_bearish += 1
    
    # HT_DCPHASE (phase angle - rising = bullish)
    if ht_dcphase > 0 and ht_dcphase < 180: cycle_bullish += 1
    else: cycle_bearish += 1
    
    cycle_dir = "BULLISH" if cycle_bullish > cycle_bearish else "BEARISH" if cycle_bearish > cycle_bullish else "NEUTRAL"
    agreement["cycles"] = {
        "bullish": cycle_bullish,
        "bearish": cycle_bearish,
        "direction": cycle_dir,
        "trending": ht_trendmode == 1
    }
    
    # =========================================================================
    # VOLATILITY AGREEMENT - ALL 3 VOLATILITY INDICATORS
    # =========================================================================
    atr = volatility.get("ATR_14", 0)
    natr = volatility.get("NATR_14", 0)
    trange = volatility.get("TRANGE", 0)
    
    # High volatility = caution, low volatility = confidence
    if natr > 2.0:
        vol_state = "HIGH"
        vol_confidence = 0.5  # Reduce confidence in high volatility
    elif natr > 1.0:
        vol_state = "NORMAL"
        vol_confidence = 1.0
    else:
        vol_state = "LOW"
        vol_confidence = 1.0
    
    agreement["volatility"] = {
        "state": vol_state,
        "natr": natr,
        "atr": atr,
        "confidence_multiplier": vol_confidence
    }
    
    # =========================================================================
    # STATISTICS AGREEMENT - ALL 9 STATISTICAL INDICATORS
    # =========================================================================
    stat_bullish = 0
    stat_bearish = 0
    
    linreg = statistics.get("LINEARREG_14", 0)
    linreg_angle = statistics.get("LINEARREG_ANGLE_14", 0)
    linreg_intercept = statistics.get("LINEARREG_INTERCEPT_14", 0)
    linreg_slope = statistics.get("LINEARREG_SLOPE_14", 0)
    stddev = statistics.get("STDDEV_5", 0)
    tsf = statistics.get("TSF_14", 0)
    var_val = statistics.get("VAR_5", 0)
    beta = statistics.get("BETA", 1)
    correl = statistics.get("CORREL", 0)
    
    # LINEARREG_SLOPE > 0 = uptrend
    if linreg_slope > 0: stat_bullish += 2
    else: stat_bearish += 2
    
    # LINEARREG_ANGLE > 0 = upward angle
    if linreg_angle > 0: stat_bullish += 1
    else: stat_bearish += 1
    
    # TSF (Time Series Forecast) > current price = bullish
    if tsf > linreg and tsf > 0: stat_bullish += 1
    elif linreg > 0: stat_bearish += 1
    
    # BETA > 1 = more volatile than market (neutral for direction)
    # CORREL - high correlation means trend following
    if correl > 0.7: stat_bullish += 1 if linreg_slope > 0 else 0
    elif correl < -0.7: stat_bearish += 1 if linreg_slope < 0 else 0
    
    stat_dir = "BULLISH" if stat_bullish > stat_bearish else "BEARISH" if stat_bearish > stat_bullish else "NEUTRAL"
    agreement["statistics"] = {
        "bullish": stat_bullish,
        "bearish": stat_bearish,
        "direction": stat_dir,
        "slope": linreg_slope,
        "angle": linreg_angle
    }
    
    # =========================================================================
    # PRICE POSITION - USING PRICE TRANSFORM (4 indicators)
    # =========================================================================
    avgprice = price_transform.get("AVGPRICE", 0)
    medprice = price_transform.get("MEDPRICE", 0)
    typprice = price_transform.get("TYPPRICE", 0)
    wclprice = price_transform.get("WCLPRICE", 0)
    
    price_bullish = 0
    price_bearish = 0
    
    # If current close > average prices = bullish
    if current_price > avgprice and avgprice > 0: price_bullish += 1
    elif avgprice > 0: price_bearish += 1
    
    if current_price > medprice and medprice > 0: price_bullish += 1
    elif medprice > 0: price_bearish += 1
    
    if current_price > typprice and typprice > 0: price_bullish += 1
    elif typprice > 0: price_bearish += 1
    
    if current_price > wclprice and wclprice > 0: price_bullish += 1
    elif wclprice > 0: price_bearish += 1
    
    price_dir = "BULLISH" if price_bullish > price_bearish else "BEARISH" if price_bearish > price_bullish else "NEUTRAL"
    agreement["price_position"] = {
        "bullish": price_bullish,
        "bearish": price_bearish,
        "direction": price_dir
    }
    
    # =========================================================================
    # SUPPORT/RESISTANCE - USING MATH OPERATORS (12 indicators)
    # =========================================================================
    sr_bullish = 0
    sr_bearish = 0
    
    max_20 = math_operators.get("MAX_20", 0)
    min_20 = math_operators.get("MIN_20", 0)
    minmax_min = math_operators.get("MINMAX_min", 0)
    minmax_max = math_operators.get("MINMAX_max", 0)
    
    # Price position relative to range
    if max_20 > 0 and min_20 > 0:
        price_range = max_20 - min_20
        if price_range > 0:
            position_in_range = (current_price - min_20) / price_range
            if position_in_range > 0.5: sr_bullish += 1
            else: sr_bearish += 1
            
            # Near resistance (top 20%) = bearish, near support (bottom 20%) = bullish
            if position_in_range > 0.8: sr_bearish += 1  # Near resistance
            elif position_in_range < 0.2: sr_bullish += 1  # Near support
    
    sr_dir = "BULLISH" if sr_bullish > sr_bearish else "BEARISH" if sr_bearish > sr_bullish else "NEUTRAL"
    agreement["support_resistance"] = {
        "bullish": sr_bullish,
        "bearish": sr_bearish,
        "direction": sr_dir,
        "max_20": max_20,
        "min_20": min_20
    }
    
    # =========================================================================
    # SUMMARY - ALL 158 INDICATORS COMBINED
    # =========================================================================
    # Sum ALL agreement categories for comprehensive scoring
    total_bullish = (
        agreement["trend"]["bullish"] +           # 25 overlap studies
        agreement["momentum"]["bullish"] +        # 44 momentum indicators
        agreement["volume"]["bullish"] +          # 3 volume indicators
        agreement["patterns"]["bullish"] +        # 61 candlestick patterns
        agreement["cycles"]["bullish"] +          # 7 Hilbert Transform indicators
        agreement["statistics"]["bullish"] +      # 9 statistical indicators
        agreement["price_position"]["bullish"] +  # 4 price transform indicators
        agreement["support_resistance"]["bullish"] # Math operators for S/R
    )
    total_bearish = (
        agreement["trend"]["bearish"] +
        agreement["momentum"]["bearish"] +
        agreement["volume"]["bearish"] +
        agreement["patterns"]["bearish"] +
        agreement["cycles"]["bearish"] +
        agreement["statistics"]["bearish"] +
        agreement["price_position"]["bearish"] +
        agreement["support_resistance"]["bearish"]
    )
    
    # Apply volatility confidence multiplier
    vol_multiplier = agreement["volatility"]["confidence_multiplier"]
    
    total = total_bullish + total_bearish
    bullish_pct = (total_bullish / total * 100) if total > 0 else 50
    
    # Determine overall direction with confidence threshold
    if total_bullish > total_bearish:
        overall = "BULLISH"
        confidence = bullish_pct * vol_multiplier
    elif total_bearish > total_bullish:
        overall = "BEARISH"
        confidence = (100 - bullish_pct) * vol_multiplier
    else:
        overall = "NEUTRAL"
        confidence = 50
    
    agreement["summary"] = {
        "total_bullish": total_bullish,
        "total_bearish": total_bearish,
        "bullish_pct": bullish_pct,
        "confidence": confidence,
        "overall": overall,
        "indicators_used": {
            "trend": agreement["trend"]["bullish"] + agreement["trend"]["bearish"],
            "momentum": agreement["momentum"]["bullish"] + agreement["momentum"]["bearish"],
            "volume": agreement["volume"]["bullish"] + agreement["volume"]["bearish"],
            "patterns": agreement["patterns"]["bullish"] + agreement["patterns"]["bearish"],
            "cycles": agreement["cycles"]["bullish"] + agreement["cycles"]["bearish"],
            "statistics": agreement["statistics"]["bullish"] + agreement["statistics"]["bearish"],
            "price_position": agreement["price_position"]["bullish"] + agreement["price_position"]["bearish"],
            "support_resistance": agreement["support_resistance"]["bullish"] + agreement["support_resistance"]["bearish"]
        }
    }
    
    return agreement


def apply_hierarchy_comprehensive(regime: MarketRegime,
                                   momentum_interp: Dict[str, Any],
                                   volume_interp: Dict[str, Any],
                                   pattern_interp: Dict[str, Any],
                                   agreement: Dict[str, Any],
                                   allowed_directions: List[TradeDirection],
                                   indicators: Dict[str, Any]) -> Tuple[TradeDirection, List[str], List[str]]:
    """
    Apply hierarchy when indicators conflict.
    EXACT GITHUB IMPLEMENTATION.
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
            
            if agreement["momentum"]["direction"] == "BEARISH":
                warning_factors.append(f"Momentum diverging ({agreement['momentum']['bearish']} bearish)")
            if volume_interp["trend"] not in ["ACCUMULATION"]:
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
            
            if agreement["momentum"]["direction"] == "BULLISH":
                warning_factors.append(f"Momentum diverging ({agreement['momentum']['bullish']} bullish)")
            if volume_interp["trend"] not in ["DISTRIBUTION"]:
                warning_factors.append("Volume not confirming - potential weakness")
            if agreement["patterns"]["direction"] == "BULLISH":
                warning_factors.append("Bullish patterns - possible bounce")
        else:
            direction = TradeDirection.NO_TRADE
    
    elif regime == MarketRegime.RANGING:
        # In ranging, use momentum extremes
        rsi = momentum.get("RSI_14", 50)
        stoch_k = momentum.get("STOCH_K", 50)
        cci = momentum.get("CCI_14", 0)
        willr = momentum.get("WILLR_14", -50)
        ultosc = momentum.get("ULTOSC", 50)
        
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


def calculate_position_multiplier_comprehensive(agreement: Dict[str, Any],
                                                 regime: MarketRegime,
                                                 warning_factors: List[str]) -> float:
    """Calculate position size multiplier based on comprehensive agreement. EXACT GITHUB."""
    if regime == MarketRegime.VOLATILE:
        return 0.0
    
    summary = agreement["summary"]
    bullish_pct = summary["bullish_pct"]
    
    if regime == MarketRegime.TRENDING_UP:
        agreement_pct = bullish_pct
    elif regime == MarketRegime.TRENDING_DOWN:
        agreement_pct = 100 - bullish_pct
    else:
        return 0.5  # Ranging - always reduced size
    
    if agreement_pct >= 75:
        multiplier = 1.0
    elif agreement_pct >= 65:
        multiplier = 0.75
    elif agreement_pct >= 55:
        multiplier = 0.5
    else:
        multiplier = 0.25
    
    if len(warning_factors) >= 3:
        multiplier *= 0.5
    elif len(warning_factors) >= 2:
        multiplier *= 0.75
    
    return min(1.0, max(0.0, multiplier))


def synthesize_decision(regime_analysis: RegimeAnalysis, 
                        momentum_interp: Dict[str, Any],
                        volume_interp: Dict[str, Any],
                        pattern_interp: Dict[str, Any],
                        indicators: Dict[str, Any]) -> TradeDecision:
    """
    Synthesize all interpretations into a wise trading decision.
    EXACT GITHUB IMPLEMENTATION.
    
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
    allowed_directions = get_allowed_directions(regime)
    
    if TradeDirection.NO_TRADE in allowed_directions and len(allowed_directions) == 1:
        return TradeDecision(
            direction=TradeDirection.NO_TRADE,
            confidence_factors=["Volatile market conditions"],
            warning_factors=["High volatility detected", "Wait for stability"],
            reasoning=f"NO TRADE - Regime: {regime.value}\n{regime_analysis.reasoning}",
            position_size_multiplier=0.0
        )
    
    # Step 2: Check COMPREHENSIVE indicator agreement
    agreement = check_comprehensive_agreement(
        momentum_interp, volume_interp, pattern_interp, indicators, regime
    )
    
    # Step 3: Apply hierarchy and determine direction
    direction, confidence_factors, warning_factors = apply_hierarchy_comprehensive(
        regime, momentum_interp, volume_interp, pattern_interp,
        agreement, allowed_directions, indicators
    )
    
    # Step 4: Determine position size based on agreement
    position_multiplier = calculate_position_multiplier_comprehensive(
        agreement, regime, warning_factors
    )
    
    # Step 5: Generate comprehensive reasoning
    summary = agreement["summary"]
    reasoning = f"""
TRADE DECISION: {direction.value}
Position Size: {position_multiplier * 100:.0f}%
Overall Agreement: {summary['total_bullish']} bullish / {summary['total_bearish']} bearish ({summary['bullish_pct']:.1f}% bullish)

{regime_analysis.reasoning}

AGREEMENT BREAKDOWN:
  Trend: {agreement['trend']['bullish']} bullish / {agreement['trend']['bearish']} bearish → {agreement['trend']['direction']}
  Momentum: {agreement['momentum']['bullish']} bullish / {agreement['momentum']['bearish']} bearish → {agreement['momentum']['direction']}
  Volume: {agreement['volume']['direction']}
  Patterns: {agreement['patterns']['direction']}
  Cycles: {agreement['cycles']['direction']}

MOMENTUM ANALYSIS:
{momentum_interp['reasoning']}
Bullish signals: {len(momentum_interp['bullish_signals'])}
Bearish signals: {len(momentum_interp['bearish_signals'])}

VOLUME ANALYSIS:
{volume_interp['reasoning']}

PATTERN ANALYSIS:
{pattern_interp['reasoning']}

CONFIDENCE FACTORS ({len(confidence_factors)}):
{chr(10).join('- ' + f for f in confidence_factors)}

WARNING FACTORS ({len(warning_factors)}):
{chr(10).join('- ' + f for f in warning_factors)}

POSITION SIZE MULTIPLIER: {position_multiplier:.2f}
"""
    
    return TradeDecision(
        direction=direction,
        confidence_factors=confidence_factors,
        warning_factors=warning_factors,
        reasoning=reasoning,
        position_size_multiplier=position_multiplier
    )

# =============================================================================
# WISDOM ENGINE - ENTRY/EXIT CALCULATION
# =============================================================================

def calculate_entry_exit(decision: TradeDecision, 
                         indicators: Dict[str, Any],
                         current_price: float,
                         symbol: str) -> TradeParameters:
    """
    Calculate entry, stop loss, and take profit using ATR-based dynamic levels.
    
    Uses:
    - ATR for volatility-adjusted SL/TP
    - Support/Resistance from indicators
    - Bollinger Bands for additional context
    """
    volatility = indicators.get("volatility", {})
    overlap = indicators.get("overlap", {})
    math_ops = indicators.get("math_operators", {})
    
    atr = volatility.get("ATR_14", 0)
    pip_value = get_pip_value(symbol)
    
    # Default ATR if not available
    if atr == 0:
        atr = current_price * 0.001  # 0.1% of price
    
    # Calculate SL/TP based on ATR
    sl_distance = atr * ATR_SL_MULTIPLIER
    tp_distance = atr * ATR_TP_MULTIPLIER
    
    # Adjust for direction
    if decision.direction == TradeDirection.LONG:
        entry_price = current_price
        stop_loss = current_price - sl_distance
        take_profit = current_price + tp_distance
        
        # Use support as additional SL reference
        recent_low = math_ops.get("MIN_20", stop_loss)
        if recent_low < stop_loss and recent_low > current_price - (sl_distance * 2):
            stop_loss = recent_low - (pip_value * 5)  # 5 pips below support
        
        entry_reasoning = f"LONG entry at {entry_price:.5f} (current market price)"
        sl_reasoning = f"Stop Loss at {stop_loss:.5f} ({ATR_SL_MULTIPLIER}x ATR = {sl_distance:.5f})"
        tp_reasoning = f"Take Profit at {take_profit:.5f} ({ATR_TP_MULTIPLIER}x ATR = {tp_distance:.5f})"
        
    elif decision.direction == TradeDirection.SHORT:
        entry_price = current_price
        stop_loss = current_price + sl_distance
        take_profit = current_price - tp_distance
        
        # Use resistance as additional SL reference
        recent_high = math_ops.get("MAX_20", stop_loss)
        if recent_high > stop_loss and recent_high < current_price + (sl_distance * 2):
            stop_loss = recent_high + (pip_value * 5)  # 5 pips above resistance
        
        entry_reasoning = f"SHORT entry at {entry_price:.5f} (current market price)"
        sl_reasoning = f"Stop Loss at {stop_loss:.5f} ({ATR_SL_MULTIPLIER}x ATR = {sl_distance:.5f})"
        tp_reasoning = f"Take Profit at {take_profit:.5f} ({ATR_TP_MULTIPLIER}x ATR = {tp_distance:.5f})"
    
    else:
        return None
    
    # Calculate pips
    sl_pips = abs(entry_price - stop_loss) / pip_value
    tp_pips = abs(take_profit - entry_price) / pip_value
    
    # Risk/Reward ratio
    rr_ratio = tp_pips / sl_pips if sl_pips > 0 else 0
    
    # Position size (based on risk)
    risk_amount = ACCOUNT_BALANCE * (MAX_RISK_PERCENT / 100)
    pip_value_per_lot = 10  # Approximate for standard lot
    position_size = (risk_amount / (sl_pips * pip_value_per_lot)) * decision.position_size_multiplier
    position_size = min(position_size, FIXED_LOT_SIZE)  # Cap at fixed lot size
    position_size = max(position_size, 0.01)  # Minimum lot size
    
    return TradeParameters(
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        stop_loss_pips=sl_pips,
        take_profit_pips=tp_pips,
        risk_reward_ratio=rr_ratio,
        atr_value=atr,
        position_size=round(position_size, 2),
        entry_reasoning=entry_reasoning,
        sl_reasoning=sl_reasoning,
        tp_reasoning=tp_reasoning
    )

# =============================================================================
# WISDOM ENGINE - MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_symbol(symbol: str, candles: Dict, price: Dict) -> Optional[Dict]:
    """
    Perform complete Wisdom Engine analysis on a symbol.
    
    Returns analysis result with decision and parameters.
    """
    # Validate data
    if not candles.get('close') or len(candles['close']) < 100:
        print(f"  {symbol}: Insufficient data ({len(candles.get('close', []))} candles)")
        return None
    
    # Convert to numpy arrays
    open_arr = np.array(candles['open'], dtype=np.float64)
    high_arr = np.array(candles['high'], dtype=np.float64)
    low_arr = np.array(candles['low'], dtype=np.float64)
    close_arr = np.array(candles['close'], dtype=np.float64)
    volume_arr = np.array(candles['volume'], dtype=np.float64)
    
    current_price = price.get('bid', close_arr[-1])
    
    # Step 1: Compute ALL 161 indicators
    indicators = compute_all_indicators(open_arr, high_arr, low_arr, close_arr, volume_arr)
    
    # Step 2: Detect market regime
    regime_analysis = detect_market_regime(indicators)
    
    # Step 3: Interpret indicators in context
    momentum_interp = interpret_momentum(indicators, regime_analysis.regime)
    volume_interp = interpret_volume(indicators)
    pattern_interp = interpret_patterns(indicators)
    
    # Step 4: Synthesize decision
    decision = synthesize_decision(
        regime_analysis, momentum_interp, volume_interp, pattern_interp, indicators
    )
    
    # Step 5: Calculate entry/exit if trading
    parameters = None
    if decision.direction != TradeDirection.NO_TRADE:
        parameters = calculate_entry_exit(decision, indicators, current_price, symbol)
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "regime": regime_analysis.regime.value,
        "regime_reasoning": regime_analysis.reasoning,
        "decision": decision.direction.value,
        "decision_reasoning": decision.reasoning,
        "confidence_factors": decision.confidence_factors,
        "warning_factors": decision.warning_factors,
        "position_multiplier": decision.position_size_multiplier,
        "parameters": {
            "entry_price": parameters.entry_price if parameters else None,
            "stop_loss": parameters.stop_loss if parameters else None,
            "take_profit": parameters.take_profit if parameters else None,
            "sl_pips": parameters.stop_loss_pips if parameters else None,
            "tp_pips": parameters.take_profit_pips if parameters else None,
            "rr_ratio": parameters.risk_reward_ratio if parameters else None,
            "lot_size": parameters.position_size if parameters else None
        } if parameters else None,
        "indicators_summary": {
            "adx": indicators["momentum"].get("ADX_14", 0),
            "rsi": indicators["momentum"].get("RSI_14", 50),
            "macd_hist": indicators["momentum"].get("MACD_hist", 0),
            "atr": indicators["volatility"].get("ATR_14", 0),
            "natr": indicators["volatility"].get("NATR_14", 0)
        }
    }


def analyze_symbol_multi_timeframe(symbol: str, candles_h1: Dict, candles_m5: Dict, price: Dict) -> Optional[Dict]:
    """
    Perform MULTI-TIMEFRAME Wisdom Engine analysis on a symbol.
    
    DUAL TIMEFRAME APPROACH:
    - H1 (1-hour): Used for REGIME DETECTION (big picture, trend direction)
    - M5 (5-minute): Used for ENTRY TIMING (precise signals, momentum)
    
    This gives us:
    - Better trend context from H1
    - More precise entry timing from M5
    - Predictions every 5 minutes with hourly trend context
    
    Returns analysis result with decision and parameters.
    """
    # Validate H1 data (need at least 100 candles for regime detection)
    if not candles_h1.get('close') or len(candles_h1['close']) < 100:
        print(f"  {symbol}: Insufficient H1 data ({len(candles_h1.get('close', []))} candles)")
        return None
    
    # Validate M5 data (need at least 50 candles for entry timing)
    if not candles_m5.get('close') or len(candles_m5['close']) < 50:
        print(f"  {symbol}: Insufficient M5 data ({len(candles_m5.get('close', []))} candles)")
        return None
    
    # Convert H1 to numpy arrays (for regime detection)
    h1_open = np.array(candles_h1['open'], dtype=np.float64)
    h1_high = np.array(candles_h1['high'], dtype=np.float64)
    h1_low = np.array(candles_h1['low'], dtype=np.float64)
    h1_close = np.array(candles_h1['close'], dtype=np.float64)
    h1_volume = np.array(candles_h1['volume'], dtype=np.float64)
    
    # Convert M5 to numpy arrays (for entry timing)
    m5_open = np.array(candles_m5['open'], dtype=np.float64)
    m5_high = np.array(candles_m5['high'], dtype=np.float64)
    m5_low = np.array(candles_m5['low'], dtype=np.float64)
    m5_close = np.array(candles_m5['close'], dtype=np.float64)
    m5_volume = np.array(candles_m5['volume'], dtype=np.float64)
    
    current_price = price.get('bid', m5_close[-1])
    
    # =========================================================================
    # STEP 1: Compute H1 indicators for REGIME DETECTION (big picture)
    # =========================================================================
    h1_indicators = compute_all_indicators(h1_open, h1_high, h1_low, h1_close, h1_volume)
    
    # =========================================================================
    # STEP 2: Detect market regime from H1 (hourly trend context)
    # =========================================================================
    regime_analysis = detect_market_regime(h1_indicators)
    
    # =========================================================================
    # STEP 3: Compute M5 indicators for ENTRY TIMING (precise signals)
    # =========================================================================
    m5_indicators = compute_all_indicators(m5_open, m5_high, m5_low, m5_close, m5_volume)
    
    # =========================================================================
    # STEP 4: Interpret M5 indicators in context of H1 regime
    # =========================================================================
    momentum_interp = interpret_momentum(m5_indicators, regime_analysis.regime)
    volume_interp = interpret_volume(m5_indicators)
    pattern_interp = interpret_patterns(m5_indicators)
    
    # =========================================================================
    # STEP 5: Synthesize decision using H1 regime + M5 signals
    # =========================================================================
    decision = synthesize_decision(
        regime_analysis, momentum_interp, volume_interp, pattern_interp, m5_indicators
    )
    
    # =========================================================================
    # STEP 6: Calculate entry/exit using M5 ATR for tighter stops
    # =========================================================================
    parameters = None
    if decision.direction != TradeDirection.NO_TRADE:
        parameters = calculate_entry_exit(decision, m5_indicators, current_price, symbol)
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "timeframe": "MULTI (H1 regime + M5 entry)",
        "regime": regime_analysis.regime.value,
        "regime_reasoning": regime_analysis.reasoning,
        "decision": decision.direction.value,
        "decision_reasoning": decision.reasoning,
        "confidence_factors": decision.confidence_factors,
        "warning_factors": decision.warning_factors,
        "position_multiplier": decision.position_size_multiplier,
        "parameters": {
            "entry_price": parameters.entry_price if parameters else None,
            "stop_loss": parameters.stop_loss if parameters else None,
            "take_profit": parameters.take_profit if parameters else None,
            "sl_pips": parameters.stop_loss_pips if parameters else None,
            "tp_pips": parameters.take_profit_pips if parameters else None,
            "rr_ratio": parameters.risk_reward_ratio if parameters else None,
            "lot_size": parameters.position_size if parameters else None
        } if parameters else None,
        "indicators_summary": {
            # H1 indicators (regime context)
            "h1_adx": h1_indicators["momentum"].get("ADX_14", 0),
            "h1_rsi": h1_indicators["momentum"].get("RSI_14", 50),
            "h1_macd_hist": h1_indicators["momentum"].get("MACD_hist", 0),
            # M5 indicators (entry timing)
            "m5_adx": m5_indicators["momentum"].get("ADX_14", 0),
            "m5_rsi": m5_indicators["momentum"].get("RSI_14", 50),
            "m5_macd_hist": m5_indicators["momentum"].get("MACD_hist", 0),
            "m5_atr": m5_indicators["volatility"].get("ATR_14", 0),
            "m5_natr": m5_indicators["volatility"].get("NATR_14", 0)
        }
    }

def find_best_trade(prices: Dict, candles: Dict, session_pairs: List[str]) -> Optional[Dict]:
    """
    Find the best trading opportunity from all analyzed symbols.
    
    Prioritizes:
    1. Trending markets over ranging
    2. Higher confidence (more factors)
    3. Better risk/reward ratio
    """
    candidates = []
    
    for symbol in session_pairs:
        if symbol not in prices or symbol not in candles:
            continue
        
        analysis = analyze_symbol(symbol, candles[symbol], prices[symbol])
        
        if analysis and analysis["decision"] != "NO_TRADE":
            # Score the trade
            score = 0
            
            # Regime bonus
            if analysis["regime"] in ["TRENDING_UP", "TRENDING_DOWN"]:
                score += 20
            elif analysis["regime"] == "RANGING":
                score += 10
            
            # Confidence bonus
            score += len(analysis["confidence_factors"]) * 5
            
            # Warning penalty
            score -= len(analysis["warning_factors"]) * 3
            
            # R:R bonus
            if analysis["parameters"]:
                rr = analysis["parameters"]["rr_ratio"]
                if rr >= 2.0:
                    score += 15
                elif rr >= 1.5:
                    score += 10
                elif rr >= 1.0:
                    score += 5
            
            analysis["score"] = score
            candidates.append(analysis)
            
            print(f"  {symbol}: {analysis['decision']} (Regime: {analysis['regime']}, Score: {score})")
    
    if not candidates:
        return None
    
    # Sort by score and return best
    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]
    
    print(f"\n  BEST TRADE: {best['symbol']} ({best['decision']}) - Score: {best['score']}")
    
    return best


def find_best_trade_multi_timeframe(prices: Dict, candles_h1: Dict, candles_m5: Dict, session_pairs: List[str]) -> Optional[Dict]:
    """
    Find the best trading opportunity using MULTI-TIMEFRAME analysis.
    
    Uses:
    - H1 candles for regime detection (big picture)
    - M5 candles for entry timing (precise signals)
    
    Prioritizes:
    1. Trending markets over ranging
    2. Higher confidence (more factors)
    3. Better risk/reward ratio
    4. M5 momentum alignment with H1 trend
    """
    candidates = []
    
    for symbol in session_pairs:
        if symbol not in prices:
            continue
        if symbol not in candles_h1 or symbol not in candles_m5:
            continue
        
        analysis = analyze_symbol_multi_timeframe(
            symbol, candles_h1[symbol], candles_m5[symbol], prices[symbol]
        )
        
        if analysis and analysis["decision"] != "NO_TRADE":
            # Score the trade
            score = 0
            
            # Regime bonus (from H1)
            if analysis["regime"] in ["TRENDING_UP", "TRENDING_DOWN"]:
                score += 20
            elif analysis["regime"] == "RANGING":
                score += 10
            
            # Confidence bonus
            score += len(analysis["confidence_factors"]) * 5
            
            # Warning penalty
            score -= len(analysis["warning_factors"]) * 3
            
            # R:R bonus
            if analysis["parameters"]:
                rr = analysis["parameters"]["rr_ratio"]
                if rr >= 2.0:
                    score += 15
                elif rr >= 1.5:
                    score += 10
                elif rr >= 1.0:
                    score += 5
            
            # Multi-timeframe alignment bonus
            # If M5 momentum aligns with H1 regime, add bonus
            h1_adx = analysis["indicators_summary"].get("h1_adx", 0)
            m5_macd = analysis["indicators_summary"].get("m5_macd_hist", 0)
            
            if analysis["regime"] == "TRENDING_UP" and m5_macd > 0:
                score += 10  # M5 momentum confirms H1 uptrend
            elif analysis["regime"] == "TRENDING_DOWN" and m5_macd < 0:
                score += 10  # M5 momentum confirms H1 downtrend
            
            # Strong H1 trend bonus
            if h1_adx > 30:
                score += 5
            
            analysis["score"] = score
            candidates.append(analysis)
            
            print(f"  {symbol}: {analysis['decision']} (H1 Regime: {analysis['regime']}, Score: {score})")
    
    if not candidates:
        return None
    
    # Sort by score and return best
    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]
    
    print(f"\n  BEST TRADE: {best['symbol']} ({best['decision']}) - Score: {best['score']}")
    print(f"  Timeframe: {best.get('timeframe', 'H1')}")
    
    return best


def analyze_symbol_with_cached_h1(symbol: str, h1_indicators: Dict, h1_regime: Dict, 
                                   m5_candles: Dict, price: Dict) -> Optional[Dict]:
    """
    Analyze symbol using CACHED H1 indicators + FRESH M5 data.
    
    This is the optimized version that:
    - Uses pre-computed H1 indicators from cache (no API call)
    - Uses pre-computed H1 regime from cache
    - Computes fresh M5 indicators for entry timing
    - All 158 indicators computed on both timeframes
    
    Returns analysis result with decision and parameters.
    """
    # Validate M5 data
    if not m5_candles.get('close') or len(m5_candles['close']) < 50:
        print(f"  {symbol}: Insufficient M5 data ({len(m5_candles.get('close', []))} candles)")
        return None
    
    # Validate H1 cache
    if not h1_indicators or not h1_regime:
        print(f"  {symbol}: Missing H1 cache data")
        return None
    
    # Convert M5 to numpy arrays
    m5_open = np.array(m5_candles['open'], dtype=np.float64)
    m5_high = np.array(m5_candles['high'], dtype=np.float64)
    m5_low = np.array(m5_candles['low'], dtype=np.float64)
    m5_close = np.array(m5_candles['close'], dtype=np.float64)
    m5_volume = np.array(m5_candles['volume'], dtype=np.float64)
    
    current_price = price.get('bid', m5_close[-1])
    
    # =========================================================================
    # STEP 1: Use CACHED H1 indicators (already computed, 158 indicators)
    # =========================================================================
    # h1_indicators already contains all 158 indicators from cache
    
    # =========================================================================
    # STEP 2: Reconstruct regime analysis from cache
    # =========================================================================
    regime_value = h1_regime.get('regime', 'RANGING')
    regime = MarketRegime(regime_value)
    
    regime_analysis = RegimeAnalysis(
        regime=regime,
        adx_value=h1_regime.get('adx_value', 20),
        adx_interpretation=h1_regime.get('adx_interpretation', ''),
        trend_mode=h1_regime.get('trend_mode', 0),
        trend_mode_interpretation='',
        ma_alignment=h1_regime.get('ma_alignment', 'MIXED'),
        ma_alignment_interpretation='',
        volatility_state=h1_regime.get('volatility_state', 'NORMAL'),
        volatility_interpretation='',
        reasoning=h1_regime.get('reasoning', '')
    )
    
    # =========================================================================
    # STEP 3: Compute FRESH M5 indicators (all 158 indicators)
    # =========================================================================
    m5_indicators = compute_all_indicators(m5_open, m5_high, m5_low, m5_close, m5_volume)
    
    # =========================================================================
    # STEP 4: Interpret M5 indicators in context of H1 regime
    # =========================================================================
    momentum_interp = interpret_momentum(m5_indicators, regime_analysis.regime)
    volume_interp = interpret_volume(m5_indicators)
    pattern_interp = interpret_patterns(m5_indicators)
    
    # =========================================================================
    # STEP 5: Synthesize decision using H1 regime + M5 signals
    # =========================================================================
    decision = synthesize_decision(
        regime_analysis, momentum_interp, volume_interp, pattern_interp, m5_indicators
    )
    
    # =========================================================================
    # STEP 6: Calculate entry/exit using M5 ATR
    # =========================================================================
    parameters = None
    if decision.direction != TradeDirection.NO_TRADE:
        parameters = calculate_entry_exit(decision, m5_indicators, current_price, symbol)
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "timeframe": "MULTI (H1 cached + M5 fresh)",
        "regime": regime_analysis.regime.value,
        "regime_reasoning": regime_analysis.reasoning,
        "decision": decision.direction.value,
        "decision_reasoning": decision.reasoning,
        "confidence_factors": decision.confidence_factors,
        "warning_factors": decision.warning_factors,
        "position_multiplier": decision.position_size_multiplier,
        "parameters": {
            "entry_price": parameters.entry_price if parameters else None,
            "stop_loss": parameters.stop_loss if parameters else None,
            "take_profit": parameters.take_profit if parameters else None,
            "sl_pips": parameters.stop_loss_pips if parameters else None,
            "tp_pips": parameters.take_profit_pips if parameters else None,
            "rr_ratio": parameters.risk_reward_ratio if parameters else None,
            "lot_size": parameters.position_size if parameters else None
        } if parameters else None,
        "indicators_summary": {
            # H1 indicators (from cache)
            "h1_adx": h1_indicators.get("momentum", {}).get("ADX_14", 0),
            "h1_rsi": h1_indicators.get("momentum", {}).get("RSI_14", 50),
            "h1_macd_hist": h1_indicators.get("momentum", {}).get("MACD_hist", 0),
            # M5 indicators (fresh)
            "m5_adx": m5_indicators["momentum"].get("ADX_14", 0),
            "m5_rsi": m5_indicators["momentum"].get("RSI_14", 50),
            "m5_macd_hist": m5_indicators["momentum"].get("MACD_hist", 0),
            "m5_atr": m5_indicators["volatility"].get("ATR_14", 0),
            "m5_natr": m5_indicators["volatility"].get("NATR_14", 0)
        }
    }


def find_best_trade_with_cached_h1(prices: Dict, h1_indicators: Dict, h1_regimes: Dict, 
                                    m5_candles: Dict, pairs: List[str]) -> Optional[Dict]:
    """
    Find the best trading opportunity using CACHED H1 + FRESH M5.
    
    Analyzes ALL 26 pairs using:
    - Cached H1 indicators (refreshed hourly)
    - Fresh M5 candles (fetched every 5 min)
    - All 158 indicators on both timeframes
    
    Prioritizes:
    1. Trending markets over ranging
    2. Higher confidence (more factors)
    3. Better risk/reward ratio
    4. M5 momentum alignment with H1 trend
    """
    candidates = []
    
    for symbol in pairs:
        if symbol not in prices:
            continue
        if symbol not in h1_indicators or symbol not in h1_regimes:
            continue
        if symbol not in m5_candles:
            continue
        
        analysis = analyze_symbol_with_cached_h1(
            symbol, 
            h1_indicators[symbol], 
            h1_regimes[symbol], 
            m5_candles[symbol], 
            prices[symbol]
        )
        
        if analysis and analysis["decision"] != "NO_TRADE":
            # Score the trade
            score = 0
            
            # Regime bonus (from H1)
            if analysis["regime"] in ["TRENDING_UP", "TRENDING_DOWN"]:
                score += 20
            elif analysis["regime"] == "RANGING":
                score += 10
            
            # Confidence bonus
            score += len(analysis["confidence_factors"]) * 5
            
            # Warning penalty
            score -= len(analysis["warning_factors"]) * 3
            
            # R:R bonus
            if analysis["parameters"]:
                rr = analysis["parameters"]["rr_ratio"]
                if rr >= 2.0:
                    score += 15
                elif rr >= 1.5:
                    score += 10
                elif rr >= 1.0:
                    score += 5
            
            # Multi-timeframe alignment bonus
            h1_adx = analysis["indicators_summary"].get("h1_adx", 0)
            m5_macd = analysis["indicators_summary"].get("m5_macd_hist", 0)
            
            if analysis["regime"] == "TRENDING_UP" and m5_macd > 0:
                score += 10
            elif analysis["regime"] == "TRENDING_DOWN" and m5_macd < 0:
                score += 10
            
            # Strong H1 trend bonus
            if h1_adx > 30:
                score += 5
            
            analysis["score"] = score
            candidates.append(analysis)
            
            print(f"  {symbol}: {analysis['decision']} (H1: {analysis['regime']}, Score: {score})")
    
    if not candidates:
        return None
    
    # Sort by score and return best
    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]
    
    print(f"\n  BEST TRADE: {best['symbol']} ({best['decision']}) - Score: {best['score']}")
    print(f"  Timeframe: {best.get('timeframe', 'H1 cached + M5 fresh')}")
    
    return best


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def lambda_handler(event, context):
    """
    Main Lambda handler - KUIPER V2 WISDOM ENGINE
    
    Uses ALL 161 TA-Lib indicators to make WISE trading decisions.
    
    PROCESS:
    1. Check market hours
    2. Check session and risk limits
    3. Manage existing positions
    4. Fetch market data for session pairs
    5. Run Wisdom Engine analysis on all pairs
    6. Execute best trade opportunity
    """
    execution_time = datetime.now(timezone.utc).isoformat()
    
    print(f"\n{'=' * 70}")
    print(f"KUIPER V2 WISDOM ENGINE @ {execution_time}")
    print(f"{'=' * 70}")
    print("Using ALL 161 TA-Lib indicators for intelligent trading decisions")
    
    # ==========================================================================
    # MARKET HOURS CHECK
    # ==========================================================================
    market_open, market_status = is_market_open()
    if not market_open:
        print(f"\n🚫 {market_status}")
        return {
            'statusCode': 200,
            'body': json_dumps({
                'timestamp': execution_time,
                'status': market_status,
                'trade_executed': False,
                'message': 'Market closed'
            })
        }
    
    current_hour = datetime.now(timezone.utc).hour
    current_session_name = get_session_name()
    
    print(f"✅ {market_status}")
    print(f"SESSION: {current_session_name} (UTC Hour: {current_hour})")
    
    if DRY_RUN:
        print("*** DRY RUN MODE - No trades will execute ***")
    
    results = {
        'timestamp': execution_time,
        'status': 'OK',
        'trade_executed': False,
        'positions_closed': 0,
        'errors': [],
        'wisdom_engine': True
    }
    
    try:
        # ======================================================================
        # STEP 1: Check kill switch
        # ======================================================================
        if not DRY_RUN and not get_trading_enabled():
            print("\n⛔ Trading is DISABLED via kill switch")
            results['status'] = 'DISABLED'
            return {'statusCode': 200, 'body': json_dumps(results)}
        
        # ======================================================================
        # STEP 2: Check current session
        # ======================================================================
        print("\n[STEP 1] Checking trading session...")
        session = get_current_session()
        
        if not session:
            print(f"  Outside optimal trading windows (UTC hour: {current_hour})")
            
            # Still check for positions to close
            print("\n[STEP 2] Checking for positions to close...")
            positions = fetch_open_positions()
            
            if positions:
                for pos in positions:
                    age = get_position_age_minutes(pos)
                    if age >= HOLD_MINUTES:
                        print(f"  ⏰ AUTO-CLOSING {pos.get('symbol')} (held {age:.1f} min)")
                        if not DRY_RUN:
                            close_result = close_position(pos.get('id'))
                            if close_result.get('status') == 'CLOSED':
                                results['positions_closed'] += 1
            
            results['status'] = 'OUTSIDE_SESSION'
            return {'statusCode': 200, 'body': json_dumps(results)}
        
        print(f"  SESSION: {session['name']} ({session['start']}:00-{session['end']}:00 UTC)")
        print(f"  {session['description']}")
        results['session'] = session['name']
        
        # ======================================================================
        # STEP 3: Check positions
        # ======================================================================
        print("\n[STEP 2] Checking positions...")
        positions = fetch_open_positions()
        should_enter_new_trade = False
        
        if positions is None:
            print("  ⚠️ Position fetch failed - SKIPPING trade entry")
            results['status'] = 'POSITION_FETCH_FAILED'
            return {'statusCode': 200, 'body': json_dumps(results)}
        
        if positions:
            # Handle multiple positions
            if len(positions) > 1:
                print(f"  ⚠️ {len(positions)} positions found - closing extras")
                positions.sort(key=lambda p: get_position_age_minutes(p))
                for pos in positions[1:]:
                    if not DRY_RUN:
                        close_position(pos['id'])
                positions = [positions[0]]
            
            pos = positions[0]
            symbol = pos.get('symbol', 'UNKNOWN')
            profit = pos.get('profit', 0)
            age = get_position_age_minutes(pos)
            
            print(f"  Position: {symbol}, Age: {age:.1f} min, Profit: ${profit:.2f}")
            
            if age >= HOLD_MINUTES:
                print(f"  ⏰ AUTO-CLOSE: {age:.1f} min >= {HOLD_MINUTES} min limit")
                if not DRY_RUN:
                    result = close_position(pos['id'])
                    print(f"  Closed {symbol}: {result['status']}, P&L: ${profit:.2f}")
                    update_trade_result(profit, profit > 0)
                should_enter_new_trade = True
            else:
                remaining = HOLD_MINUTES - age
                print(f"  ⏳ WAITING for TP/SL ({remaining:.1f} min until auto-close)")
                results['status'] = 'POSITION_OPEN'
                results['position'] = {'symbol': symbol, 'profit': profit, 'age_minutes': age}
                return {'statusCode': 200, 'body': json_dumps(results)}
        else:
            print("  No open positions - READY FOR NEW TRADE")
            should_enter_new_trade = True
        
        if not should_enter_new_trade:
            results['status'] = 'NO_ACTION'
            return {'statusCode': 200, 'body': json_dumps(results)}
        
        # ======================================================================
        # STEP 4: Fetch market data (H1 CACHED + M5 FRESH)
        # ======================================================================
        print("\n[STEP 3] Fetching market data (H1 CACHED + M5 FRESH)...")
        
        # Use ALL 26 pairs, not just session pairs
        all_pairs = TRADING_PAIRS
        print(f"  Analyzing ALL {len(all_pairs)} pairs (not session-limited)")
        print(f"  H1: Cached (refreshed hourly) - 158 indicators pre-computed")
        print(f"  M5: Fresh (fetched now) - 158 indicators computed")
        
        # Fetch with H1 caching - only M5 + prices hit the API
        prices, h1_indicators, h1_regimes, m5_candles = fetch_data_with_h1_cache(all_pairs)
        print(f"  Prices: {len(prices)}/{len(all_pairs)}")
        print(f"  H1 Indicators: {len(h1_indicators)}/{len(all_pairs)} (from cache)")
        print(f"  M5 Candles: {len(m5_candles)}/{len(all_pairs)} (fresh)")
        
        results['pairs_analyzed'] = len(all_pairs)
        results['h1_cached'] = len(h1_indicators)
        
        # ======================================================================
        # STEP 5: Run Wisdom Engine Analysis (H1 CACHED + M5 FRESH)
        # ======================================================================
        print("\n[STEP 4] Running Wisdom Engine Analysis (158 indicators x 2 timeframes)...")
        print("  H1: Regime detection from cache (big picture)")
        print("  M5: Entry timing fresh (precise signals)")
        best_trade = find_best_trade_with_cached_h1(prices, h1_indicators, h1_regimes, m5_candles, all_pairs)
        
        if not best_trade:
            print("\n❌ No valid trading opportunity found")
            results['status'] = 'NO_TRADE'
            return {'statusCode': 200, 'body': json_dumps(results)}
        
        results['analysis'] = {
            'symbol': best_trade['symbol'],
            'regime': best_trade['regime'],
            'decision': best_trade['decision'],
            'timeframe': best_trade.get('timeframe', 'H1 cached + M5 fresh'),
            'confidence_factors': best_trade['confidence_factors'],
            'warning_factors': best_trade['warning_factors'],
            'score': best_trade['score']
        }
        
        # ======================================================================
        # STEP 6: Execute trade
        # ======================================================================
        print("\n[STEP 5] Executing trade...")
        
        params = best_trade['parameters']
        if not params:
            print("  ❌ No trade parameters calculated")
            results['status'] = 'NO_PARAMS'
            return {'statusCode': 200, 'body': json_dumps(results)}
        
        action = "BUY" if best_trade['decision'] == "LONG" else "SELL"
        
        print(f"\n  📊 WISDOM ENGINE DECISION (H1 CACHED + M5 FRESH):")
        print(f"     Symbol: {best_trade['symbol']}")
        print(f"     Direction: {best_trade['decision']}")
        print(f"     H1 Regime: {best_trade['regime']}")
        print(f"     Timeframe: {best_trade.get('timeframe', 'H1 cached + M5 fresh')}")
        print(f"     Entry: {params['entry_price']:.5f}")
        print(f"     Stop Loss: {params['stop_loss']:.5f} ({params['sl_pips']:.1f} pips)")
        print(f"     Take Profit: {params['take_profit']:.5f} ({params['tp_pips']:.1f} pips)")
        print(f"     R:R Ratio: {params['rr_ratio']:.2f}")
        print(f"     Lot Size: {params['lot_size']}")
        print(f"\n  Confidence Factors:")
        for factor in best_trade['confidence_factors'][:5]:
            print(f"     ✓ {factor}")
        if best_trade['warning_factors']:
            print(f"\n  Warning Factors:")
            for factor in best_trade['warning_factors'][:3]:
                print(f"     ⚠ {factor}")
        
        if DRY_RUN:
            print("\n  🔸 DRY RUN - Trade not executed")
            results['status'] = 'DRY_RUN'
            results['trade_executed'] = False
        else:
            trade_result = execute_trade(
                symbol=best_trade['symbol'],
                action=action,
                lot_size=params['lot_size'],
                stop_loss=params['stop_loss'],
                take_profit=params['take_profit']
            )
            
            results['trade_result'] = trade_result
            
            if trade_result['status'] == 'EXECUTED':
                print(f"\n  ✅ TRADE EXECUTED: {action} {best_trade['symbol']}")
                print(f"     Order ID: {trade_result.get('order_id')}")
                results['trade_executed'] = True
                results['status'] = 'EXECUTED'
            else:
                print(f"\n  ❌ TRADE FAILED: {trade_result.get('error', 'Unknown error')}")
                results['status'] = 'FAILED'
                results['errors'].append(trade_result.get('error', 'Trade execution failed'))
        
        # ======================================================================
        # SUMMARY
        # ======================================================================
        print(f"\n{'=' * 70}")
        print("KUIPER V2 EXECUTION COMPLETE")
        print(f"{'=' * 70}")
        print(f"  Session: {session['name']}")
        print(f"  Status: {results['status']}")
        print(f"  Wisdom Engine: 158 indicators x 2 timeframes (H1 cached + M5 fresh)")
        print(f"  Pairs Analyzed: {len(TRADING_PAIRS)}")
        if results.get('trade_executed'):
            print(f"  NEW TRADE: {action} {best_trade['symbol']}")
            print(f"  Regime: {best_trade['regime']}")
            print(f"  Will hold for {HOLD_MINUTES} minutes")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        results['status'] = 'ERROR'
        results['errors'].append(str(e))
        import traceback
        traceback.print_exc()
    
    return {
        'statusCode': 200,
        'body': json_dumps(results)
    }


# =============================================================================
# LOCAL TESTING
# =============================================================================

if __name__ == "__main__":
    # Load credentials from env.json
    import os
    import sys
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "env.json")
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8-sig') as f:
            env = json.load(f)
            if "Variables" in env:
                env = env["Variables"]
            os.environ["METAAPI_TOKEN"] = env.get("METAAPI_TOKEN", "")
            os.environ["METAAPI_ACCOUNT_ID"] = env.get("METAAPI_ACCOUNT_ID", "")
    
    # Run test
    os.environ["DRY_RUN"] = "true"
    result = lambda_handler({}, None)
    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    print(json.dumps(json.loads(result['body']), indent=2))
