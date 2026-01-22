"""
Kuiper V2 Data Layer
====================
Fetches OHLCV data from MetaAPI with caching and retry logic.

MetaAPI Response Format:
[
    {
        "time": "2024-01-15T10:00:00.000Z",
        "open": 1.08500,
        "high": 1.08550,
        "low": 1.08480,
        "close": 1.08520,
        "tickVolume": 1234
    },
    ...
]
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import numpy as np

from .config import (
    METAAPI_TOKEN,
    METAAPI_ACCOUNT_ID,
    METAAPI_MARKET_DATA_URL,
    DEFAULT_CANDLE_COUNT,
    CACHE_TTL_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF_BASE,
    SUPPORTED_TIMEFRAMES
)


class OHLCVData:
    """Container for OHLCV data with numpy arrays for TA-Lib compatibility."""
    
    def __init__(self, 
                 open_: np.ndarray,
                 high: np.ndarray,
                 low: np.ndarray,
                 close: np.ndarray,
                 volume: np.ndarray,
                 time: List[str]):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.time = time
    
    def __len__(self) -> int:
        return len(self.close)
    
    def is_valid(self) -> bool:
        """Check if data has minimum required candles."""
        return len(self.close) >= 100  # Minimum for most indicators
    
    @property
    def latest_close(self) -> float:
        """Get the most recent close price."""
        return float(self.close[-1]) if len(self.close) > 0 else 0.0
    
    @property
    def latest_time(self) -> str:
        """Get the most recent candle time."""
        return self.time[-1] if self.time else ""


class DataLayerCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, ttl_seconds: int = CACHE_TTL_SECONDS):
        self._cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[OHLCVData]:
        """Get cached data if not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, data: OHLCVData) -> None:
        """Cache data with current timestamp."""
        self._cache[key] = (data, time.time())
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()


class DataLayer:
    """
    Fetches and caches OHLCV data from MetaAPI.
    
    Usage:
        data_layer = DataLayer()
        ohlcv = data_layer.get_ohlcv("EURUSD", "H1", bars=500)
        
        # Access numpy arrays for TA-Lib
        close = ohlcv.close  # np.ndarray
        high = ohlcv.high    # np.ndarray
    """
    
    def __init__(self, 
                 token: str = METAAPI_TOKEN,
                 account_id: str = METAAPI_ACCOUNT_ID):
        self.token = token
        self.account_id = account_id
        self.base_url = METAAPI_MARKET_DATA_URL
        self._cache = DataLayerCache()
    
    def _make_request(self, url: str) -> Optional[List[Dict]]:
        """Make HTTP request with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(url)
                req.add_header("auth-token", self.token)
                req.add_header("Accept", "application/json")
                req.add_header("Content-Type", "application/json")
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode())
                    
            except urllib.error.HTTPError as e:
                print(f"HTTP Error {e.code} fetching {url}: {e.reason}")
                if e.code == 429:  # Rate limited
                    wait_time = RETRY_BACKOFF_BASE ** (attempt + 2)
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif e.code >= 500:  # Server error, retry
                    wait_time = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(wait_time)
                else:
                    return None
                    
            except urllib.error.URLError as e:
                print(f"URL Error fetching {url}: {e.reason}")
                wait_time = RETRY_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                wait_time = RETRY_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
        
        return None
    
    def _parse_candles(self, candles: List[Dict]) -> OHLCVData:
        """Parse MetaAPI candle response into OHLCVData."""
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        times = []
        
        for c in candles:
            if c.get('close') is not None:
                opens.append(float(c.get('open', c['close'])))
                highs.append(float(c.get('high', c['close'])))
                lows.append(float(c.get('low', c['close'])))
                closes.append(float(c['close']))
                volumes.append(float(c.get('tickVolume', 0)))
                times.append(c.get('time', ''))
        
        return OHLCVData(
            open_=np.array(opens, dtype=np.float64),
            high=np.array(highs, dtype=np.float64),
            low=np.array(lows, dtype=np.float64),
            close=np.array(closes, dtype=np.float64),
            volume=np.array(volumes, dtype=np.float64),
            time=times
        )
    
    def get_ohlcv(self, 
                  symbol: str, 
                  timeframe: str = "H1",
                  bars: int = DEFAULT_CANDLE_COUNT) -> OHLCVData:
        """
        Fetch OHLCV data for a symbol.
        
        Args:
            symbol: Currency pair (e.g., "EURUSD")
            timeframe: Candle timeframe (M1, M5, M15, M30, H1, H4, D1)
            bars: Number of candles to fetch (minimum 500 recommended)
        
        Returns:
            OHLCVData with numpy arrays for open, high, low, close, volume
        """
        # Validate timeframe
        tf_map = {
            "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
            "H1": "1h", "H4": "4h", "D1": "1d"
        }
        tf = tf_map.get(timeframe, timeframe.lower())
        
        # Check cache
        cache_key = f"{symbol}_{tf}_{bars}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Fetch from API
        url = (f"{self.base_url}/users/current/accounts/{self.account_id}"
               f"/historical-market-data/symbols/{symbol}/timeframes/{tf}"
               f"/candles?limit={bars}")
        
        candles = self._make_request(url)
        
        if candles is None or len(candles) == 0:
            print(f"No data returned for {symbol} {timeframe}")
            return self._empty_ohlcv()
        
        ohlcv = self._parse_candles(candles)
        
        # Cache the result
        self._cache.set(cache_key, ohlcv)
        
        return ohlcv
    
    def get_multi_timeframe(self, 
                            symbol: str,
                            timeframes: List[str]) -> Dict[str, OHLCVData]:
        """
        Fetch OHLCV for multiple timeframes.
        
        Args:
            symbol: Currency pair
            timeframes: List of timeframes to fetch
        
        Returns:
            Dict mapping timeframe to OHLCVData
        """
        results = {}
        for tf in timeframes:
            results[tf] = self.get_ohlcv(symbol, tf)
        return results
    
    def get_multiple_symbols(self,
                             symbols: List[str],
                             timeframe: str = "H1",
                             bars: int = DEFAULT_CANDLE_COUNT) -> Dict[str, OHLCVData]:
        """
        Fetch OHLCV for multiple symbols in parallel.
        
        Args:
            symbols: List of currency pairs
            timeframe: Candle timeframe
            bars: Number of candles
        
        Returns:
            Dict mapping symbol to OHLCVData
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(self.get_ohlcv, sym, timeframe, bars): sym 
                for sym in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    results[symbol] = self._empty_ohlcv()
        
        return results
    
    def _empty_ohlcv(self) -> OHLCVData:
        """Return empty OHLCVData for error cases."""
        return OHLCVData(
            open_=np.array([], dtype=np.float64),
            high=np.array([], dtype=np.float64),
            low=np.array([], dtype=np.float64),
            close=np.array([], dtype=np.float64),
            volume=np.array([], dtype=np.float64),
            time=[]
        )
    
    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()
