"""
Kuiper V2 Configuration
=======================
All configurable parameters loaded from environment variables with sensible defaults.
"""

import os
from typing import List

# =============================================================================
# METAAPI CONFIGURATION
# =============================================================================
METAAPI_TOKEN = os.environ.get("METAAPI_TOKEN", "")
METAAPI_ACCOUNT_ID = os.environ.get("METAAPI_ACCOUNT_ID", "")
METAAPI_BASE_URL = "https://mt-client-api-v1.new-york.agiliumtrade.ai"
METAAPI_MARKET_DATA_URL = "https://mt-market-data-client-api-v1.new-york.agiliumtrade.ai"

# =============================================================================
# DATA FETCHING
# =============================================================================
DEFAULT_CANDLE_COUNT = 500  # Minimum candles for accurate indicator computation
CACHE_TTL_SECONDS = 60  # Cache data for 60 seconds
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # Exponential backoff: 2^retry seconds

# =============================================================================
# TRADING SYMBOLS
# =============================================================================
DEFAULT_SYMBOLS: List[str] = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
    "USDCHF", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"
]

SYMBOLS = os.environ.get("SYMBOLS", ",".join(DEFAULT_SYMBOLS)).split(",")

# =============================================================================
# TIMEFRAMES
# =============================================================================
DEFAULT_TIMEFRAME = os.environ.get("TIMEFRAME", "H1")
SUPPORTED_TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]

# =============================================================================
# INDICATOR PARAMETERS (Configurable)
# =============================================================================

# Moving Averages
SMA_PERIODS = [int(x) for x in os.environ.get("SMA_PERIODS", "20,50,200").split(",")]
EMA_PERIODS = [int(x) for x in os.environ.get("EMA_PERIODS", "12,26,50").split(",")]

# RSI
RSI_PERIOD = int(os.environ.get("RSI_PERIOD", "14"))

# MACD
MACD_FAST = int(os.environ.get("MACD_FAST", "12"))
MACD_SLOW = int(os.environ.get("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.environ.get("MACD_SIGNAL", "9"))

# ADX
ADX_PERIOD = int(os.environ.get("ADX_PERIOD", "14"))

# Bollinger Bands
BBANDS_PERIOD = int(os.environ.get("BBANDS_PERIOD", "20"))
BBANDS_STDDEV = float(os.environ.get("BBANDS_STDDEV", "2.0"))

# ATR
ATR_PERIOD = int(os.environ.get("ATR_PERIOD", "14"))

# Stochastic
STOCH_FASTK = int(os.environ.get("STOCH_FASTK", "5"))
STOCH_SLOWK = int(os.environ.get("STOCH_SLOWK", "3"))
STOCH_SLOWD = int(os.environ.get("STOCH_SLOWD", "3"))

# =============================================================================
# RISK MANAGEMENT
# =============================================================================
ATR_SL_MULTIPLIER = float(os.environ.get("ATR_SL_MULTIPLIER", "1.5"))
ATR_TP_MULTIPLIER = float(os.environ.get("ATR_TP_MULTIPLIER", "2.5"))
MAX_RISK_PERCENT = float(os.environ.get("MAX_RISK_PERCENT", "2.0"))

# =============================================================================
# MARKET REGIME THRESHOLDS
# =============================================================================
ADX_TRENDING_THRESHOLD = int(os.environ.get("ADX_TRENDING_THRESHOLD", "25"))
ADX_WEAK_THRESHOLD = int(os.environ.get("ADX_WEAK_THRESHOLD", "20"))

# =============================================================================
# AWS CONFIGURATION
# =============================================================================
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "kuiper-v2-trades")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# =============================================================================
# PERFORMANCE
# =============================================================================
MAX_PROCESSING_TIME_SINGLE = 5  # seconds per symbol
MAX_PROCESSING_TIME_TOTAL = 30  # seconds for all symbols
LAMBDA_MEMORY_MB = 1024
