"""
Kuiper V2 Trade Executor
========================
Executes trades via MetaAPI based on Wisdom Engine decisions.

Features:
- Place market orders with SL/TP
- Check existing positions
- Prevent duplicate positions
- Close positions
- Full trade logging with reasoning
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import time

from .config import (
    METAAPI_TOKEN,
    METAAPI_ACCOUNT_ID,
    METAAPI_BASE_URL,
    MAX_RETRIES,
    RETRY_BACKOFF_BASE
)
from .models import TradeDecision, TradeParameters, TradeResult, TradeDirection


class Position:
    """Represents an open trading position."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.symbol = data.get("symbol", "")
        self.type = data.get("type", "")  # "POSITION_TYPE_BUY" or "POSITION_TYPE_SELL"
        self.volume = data.get("volume", 0)
        self.open_price = data.get("openPrice", 0)
        self.current_price = data.get("currentPrice", 0)
        self.profit = data.get("profit", 0)
        self.stop_loss = data.get("stopLoss", 0)
        self.take_profit = data.get("takeProfit", 0)
        self.time = data.get("time", "")
        self.comment = data.get("comment", "")
    
    @property
    def direction(self) -> str:
        """Get position direction as LONG or SHORT."""
        if "BUY" in self.type:
            return "LONG"
        elif "SELL" in self.type:
            return "SHORT"
        return "UNKNOWN"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "direction": self.direction,
            "volume": self.volume,
            "open_price": self.open_price,
            "current_price": self.current_price,
            "profit": self.profit,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "time": self.time
        }


class TradeExecutor:
    """
    Executes trades via MetaAPI.
    
    Usage:
        executor = TradeExecutor()
        
        # Check positions
        positions = executor.get_positions("EURUSD")
        
        # Execute trade
        result = executor.execute(decision, parameters, "EURUSD")
        
        # Close position
        executor.close_position(position_id, "Take profit reached")
    """
    
    def __init__(self,
                 token: str = METAAPI_TOKEN,
                 account_id: str = METAAPI_ACCOUNT_ID,
                 dry_run: bool = False):
        """
        Initialize Trade Executor.
        
        Args:
            token: MetaAPI token
            account_id: MetaAPI account ID
            dry_run: If True, don't actually execute trades (for testing)
        """
        self.token = token
        self.account_id = account_id
        self.base_url = METAAPI_BASE_URL
        self.dry_run = dry_run
        self._trade_log: List[Dict] = []
    
    def _make_request(self, url: str, method: str = "GET", 
                      data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to MetaAPI."""
        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(url, method=method)
                req.add_header("auth-token", self.token)
                req.add_header("Accept", "application/json")
                req.add_header("Content-Type", "application/json")
                
                body = None
                if data:
                    body = json.dumps(data).encode('utf-8')
                
                with urllib.request.urlopen(req, data=body, timeout=30) as response:
                    response_text = response.read().decode()
                    if response_text:
                        return json.loads(response_text)
                    return {"success": True}
                    
            except urllib.error.HTTPError as e:
                error_body = e.read().decode() if e.fp else ""
                print(f"HTTP Error {e.code}: {e.reason}")
                print(f"Response: {error_body}")
                
                if e.code == 429:  # Rate limited
                    wait_time = RETRY_BACKOFF_BASE ** (attempt + 2)
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif e.code >= 500:  # Server error
                    wait_time = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(wait_time)
                else:
                    return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body}
                    
            except Exception as e:
                print(f"Error: {e}")
                wait_time = RETRY_BACKOFF_BASE ** attempt
                time.sleep(wait_time)
        
        return None
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """
        Get current open positions.
        
        Args:
            symbol: Filter by symbol (optional)
        
        Returns:
            List of Position objects
        """
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/positions"
        
        response = self._make_request(url)
        
        if response is None or "error" in response:
            print(f"Failed to get positions: {response}")
            return []
        
        positions = []
        for pos_data in response if isinstance(response, list) else []:
            pos = Position(pos_data)
            if symbol is None or pos.symbol == symbol:
                positions.append(pos)
        
        return positions
    
    def has_position(self, symbol: str, direction: str) -> bool:
        """
        Check if there's already a position in the given direction.
        
        Args:
            symbol: Trading symbol
            direction: "LONG" or "SHORT"
        
        Returns:
            True if position exists
        """
        positions = self.get_positions(symbol)
        for pos in positions:
            if pos.direction == direction:
                return True
        return False
    
    def execute(self, 
                decision: TradeDecision,
                parameters: TradeParameters,
                symbol: str,
                reasoning: str = "") -> TradeResult:
        """
        Execute a trade based on the decision.
        
        Args:
            decision: TradeDecision from Wisdom Engine
            parameters: TradeParameters with entry/SL/TP
            symbol: Trading symbol
            reasoning: Full reasoning for the trade
        
        Returns:
            TradeResult with execution details
        """
        timestamp = datetime.now(timezone.utc)
        
        # Check if we should trade
        if decision.direction == TradeDirection.NO_TRADE:
            return TradeResult(
                success=False,
                order_id=None,
                symbol=symbol,
                direction="NO_TRADE",
                entry_price=0,
                stop_loss=0,
                take_profit=0,
                lot_size=0,
                error_message="No trade signal",
                timestamp=timestamp
            )
        
        direction = decision.direction.value
        
        # Check for duplicate position
        if self.has_position(symbol, direction):
            return TradeResult(
                success=False,
                order_id=None,
                symbol=symbol,
                direction=direction,
                entry_price=parameters.entry_price,
                stop_loss=parameters.stop_loss,
                take_profit=parameters.take_profit,
                lot_size=parameters.position_size,
                error_message=f"Already have {direction} position on {symbol}",
                timestamp=timestamp
            )
        
        # Prepare order
        action_type = "ORDER_TYPE_BUY" if direction == "LONG" else "ORDER_TYPE_SELL"
        
        order_data = {
            "symbol": symbol,
            "actionType": action_type,
            "volume": parameters.position_size,
            "stopLoss": parameters.stop_loss,
            "takeProfit": parameters.take_profit,
            "comment": f"Kuiper-V2 {direction}"
        }
        
        # Log the trade attempt
        trade_log_entry = {
            "timestamp": timestamp.isoformat(),
            "symbol": symbol,
            "direction": direction,
            "entry_price": parameters.entry_price,
            "stop_loss": parameters.stop_loss,
            "take_profit": parameters.take_profit,
            "lot_size": parameters.position_size,
            "reasoning": reasoning,
            "dry_run": self.dry_run
        }
        self._trade_log.append(trade_log_entry)
        
        # Dry run mode
        if self.dry_run:
            print(f"[DRY RUN] Would execute {direction} {symbol}")
            print(f"  Entry: {parameters.entry_price}")
            print(f"  SL: {parameters.stop_loss}")
            print(f"  TP: {parameters.take_profit}")
            print(f"  Size: {parameters.position_size} lots")
            
            return TradeResult(
                success=True,
                order_id="DRY_RUN_" + str(int(timestamp.timestamp())),
                symbol=symbol,
                direction=direction,
                entry_price=parameters.entry_price,
                stop_loss=parameters.stop_loss,
                take_profit=parameters.take_profit,
                lot_size=parameters.position_size,
                error_message=None,
                timestamp=timestamp
            )
        
        # Execute real trade
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/trade"
        
        response = self._make_request(url, method="POST", data=order_data)
        
        if response is None:
            return TradeResult(
                success=False,
                order_id=None,
                symbol=symbol,
                direction=direction,
                entry_price=parameters.entry_price,
                stop_loss=parameters.stop_loss,
                take_profit=parameters.take_profit,
                lot_size=parameters.position_size,
                error_message="Failed to execute trade - no response",
                timestamp=timestamp
            )
        
        if "error" in response:
            return TradeResult(
                success=False,
                order_id=None,
                symbol=symbol,
                direction=direction,
                entry_price=parameters.entry_price,
                stop_loss=parameters.stop_loss,
                take_profit=parameters.take_profit,
                lot_size=parameters.position_size,
                error_message=str(response.get("error", "Unknown error")),
                timestamp=timestamp
            )
        
        # Success
        order_id = response.get("orderId", response.get("positionId", "unknown"))
        
        return TradeResult(
            success=True,
            order_id=str(order_id),
            symbol=symbol,
            direction=direction,
            entry_price=parameters.entry_price,
            stop_loss=parameters.stop_loss,
            take_profit=parameters.take_profit,
            lot_size=parameters.position_size,
            error_message=None,
            timestamp=timestamp
        )
    
    def close_position(self, position_id: str, reason: str = "") -> Dict[str, Any]:
        """
        Close an existing position.
        
        Args:
            position_id: Position ID to close
            reason: Reason for closing
        
        Returns:
            Dict with result
        """
        if self.dry_run:
            print(f"[DRY RUN] Would close position {position_id}")
            print(f"  Reason: {reason}")
            return {"success": True, "dry_run": True}
        
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/trade"
        
        close_data = {
            "actionType": "POSITION_CLOSE_ID",
            "positionId": position_id,
            "comment": f"Kuiper-V2: {reason}"
        }
        
        response = self._make_request(url, method="POST", data=close_data)
        
        if response is None or "error" in response:
            return {"success": False, "error": response}
        
        return {"success": True, "response": response}
    
    def modify_position(self, position_id: str, 
                        stop_loss: Optional[float] = None,
                        take_profit: Optional[float] = None) -> Dict[str, Any]:
        """
        Modify stop loss or take profit of an existing position.
        
        Args:
            position_id: Position ID to modify
            stop_loss: New stop loss (optional)
            take_profit: New take profit (optional)
        
        Returns:
            Dict with result
        """
        if self.dry_run:
            print(f"[DRY RUN] Would modify position {position_id}")
            print(f"  New SL: {stop_loss}")
            print(f"  New TP: {take_profit}")
            return {"success": True, "dry_run": True}
        
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/trade"
        
        modify_data = {
            "actionType": "POSITION_MODIFY",
            "positionId": position_id
        }
        
        if stop_loss is not None:
            modify_data["stopLoss"] = stop_loss
        if take_profit is not None:
            modify_data["takeProfit"] = take_profit
        
        response = self._make_request(url, method="POST", data=modify_data)
        
        if response is None or "error" in response:
            return {"success": False, "error": response}
        
        return {"success": True, "response": response}
    
    def get_trade_log(self) -> List[Dict]:
        """Get the trade log."""
        return self._trade_log.copy()
    
    def clear_trade_log(self) -> None:
        """Clear the trade log."""
        self._trade_log.clear()
