"""
Kuiper V2 Lambda Handler
========================
Main entry point for AWS Lambda execution.

This handler:
1. Initializes all components (DataLayer, Indicators, WisdomEngine, TradeExecutor)
2. Processes configured symbols in parallel
3. Stores results in DynamoDB
4. Sends SNS alerts for executed trades
5. Logs metrics to CloudWatch
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# AWS SDK (optional - for DynamoDB and SNS)
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from .config import (
    SYMBOLS, DEFAULT_TIMEFRAME, DYNAMODB_TABLE, SNS_TOPIC_ARN,
    MAX_PROCESSING_TIME_SINGLE, MAX_PROCESSING_TIME_TOTAL
)
from .data_layer import DataLayer
from .indicators import compute_all_indicators
from .wisdom_engine import WisdomEngine
from .trade_executor import TradeExecutor
from .models import MarketAnalysis, TradeResult, TradeDirection


class KuiperEngine:
    """
    Main Kuiper V2 Trading Engine.
    
    Orchestrates all components for market analysis and trade execution.
    """
    
    def __init__(self, 
                 dry_run: bool = True,
                 account_balance: float = 10000.0):
        """
        Initialize Kuiper Engine.
        
        Args:
            dry_run: If True, don't execute real trades
            account_balance: Account balance for position sizing
        """
        self.dry_run = dry_run
        self.account_balance = account_balance
        
        # Initialize components
        self.data_layer = DataLayer()
        self.wisdom_engine = WisdomEngine(account_balance=account_balance)
        self.trade_executor = TradeExecutor(dry_run=dry_run)
        
        # AWS clients (if available)
        self.dynamodb = None
        self.sns = None
        if HAS_BOTO3:
            try:
                self.dynamodb = boto3.resource('dynamodb')
                self.sns = boto3.client('sns')
            except Exception as e:
                print(f"Warning: Could not initialize AWS clients: {e}")
    
    def process_symbol(self, symbol: str, timeframe: str = DEFAULT_TIMEFRAME) -> Dict[str, Any]:
        """
        Process a single symbol through the complete pipeline.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Candle timeframe
        
        Returns:
            Dict with analysis and trade results
        """
        start_time = time.time()
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "error": None,
            "analysis": None,
            "trade_result": None,
            "processing_time": 0
        }
        
        try:
            # Step 1: Fetch OHLCV data
            ohlcv = self.data_layer.get_ohlcv(symbol, timeframe, bars=500)
            
            if not ohlcv.is_valid():
                result["error"] = f"Invalid OHLCV data for {symbol}"
                return result
            
            # Step 2: Compute all indicators
            indicators = compute_all_indicators(
                ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume
            )
            
            # Step 3: Run Wisdom Engine analysis
            analysis = self.wisdom_engine.analyze(
                indicators=indicators,
                current_price=ohlcv.latest_close,
                symbol=symbol,
                timeframe=timeframe
            )
            
            result["analysis"] = analysis.to_dict()
            
            # Step 4: Execute trade if signal
            if analysis.decision.direction != TradeDirection.NO_TRADE and analysis.parameters:
                trade_result = self.trade_executor.execute(
                    decision=analysis.decision,
                    parameters=analysis.parameters,
                    symbol=symbol,
                    reasoning=analysis.decision.reasoning
                )
                
                result["trade_result"] = {
                    "success": trade_result.success,
                    "order_id": trade_result.order_id,
                    "direction": trade_result.direction,
                    "entry_price": trade_result.entry_price,
                    "stop_loss": trade_result.stop_loss,
                    "take_profit": trade_result.take_profit,
                    "lot_size": trade_result.lot_size,
                    "error": trade_result.error_message
                }
                
                # Send SNS alert if trade executed
                if trade_result.success and not self.dry_run:
                    self._send_trade_alert(symbol, analysis, trade_result)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            print(f"Error processing {symbol}: {e}")
        
        result["processing_time"] = time.time() - start_time
        return result
    
    def process_all_symbols(self, 
                            symbols: Optional[List[str]] = None,
                            timeframe: str = DEFAULT_TIMEFRAME,
                            parallel: bool = True) -> Dict[str, Any]:
        """
        Process all configured symbols.
        
        Args:
            symbols: List of symbols to process (default: from config)
            timeframe: Candle timeframe
            parallel: Process symbols in parallel
        
        Returns:
            Dict with all results
        """
        if symbols is None:
            symbols = SYMBOLS
        
        start_time = time.time()
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbols_processed": 0,
            "trades_executed": 0,
            "errors": 0,
            "total_processing_time": 0,
            "results": {}
        }
        
        if parallel:
            # Process in parallel
            with ThreadPoolExecutor(max_workers=min(10, len(symbols))) as executor:
                future_to_symbol = {
                    executor.submit(self.process_symbol, sym, timeframe): sym
                    for sym in symbols
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result(timeout=MAX_PROCESSING_TIME_SINGLE)
                        results["results"][symbol] = result
                        results["symbols_processed"] += 1
                        
                        if result.get("trade_result", {}).get("success"):
                            results["trades_executed"] += 1
                        if result.get("error"):
                            results["errors"] += 1
                            
                    except Exception as e:
                        results["results"][symbol] = {
                            "symbol": symbol,
                            "success": False,
                            "error": str(e)
                        }
                        results["errors"] += 1
        else:
            # Process sequentially
            for symbol in symbols:
                result = self.process_symbol(symbol, timeframe)
                results["results"][symbol] = result
                results["symbols_processed"] += 1
                
                if result.get("trade_result", {}).get("success"):
                    results["trades_executed"] += 1
                if result.get("error"):
                    results["errors"] += 1
        
        results["total_processing_time"] = time.time() - start_time
        
        # Store results in DynamoDB
        if not self.dry_run:
            self._store_results(results)
        
        return results
    
    def _send_trade_alert(self, symbol: str, analysis: MarketAnalysis, 
                          trade_result: TradeResult) -> None:
        """Send SNS alert for executed trade."""
        if not self.sns or not SNS_TOPIC_ARN:
            return
        
        try:
            message = {
                "symbol": symbol,
                "direction": trade_result.direction,
                "entry_price": trade_result.entry_price,
                "stop_loss": trade_result.stop_loss,
                "take_profit": trade_result.take_profit,
                "lot_size": trade_result.lot_size,
                "regime": analysis.regime.value,
                "reasoning_summary": analysis.decision.confidence_factors[:3],
                "timestamp": trade_result.timestamp.isoformat()
            }
            
            self.sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"Kuiper V2 Trade: {trade_result.direction} {symbol}",
                Message=json.dumps(message, indent=2)
            )
        except Exception as e:
            print(f"Failed to send SNS alert: {e}")
    
    def _store_results(self, results: Dict[str, Any]) -> None:
        """Store results in DynamoDB."""
        if not self.dynamodb or not DYNAMODB_TABLE:
            return
        
        try:
            table = self.dynamodb.Table(DYNAMODB_TABLE)
            
            # Store summary
            table.put_item(Item={
                "pk": f"SUMMARY#{results['timestamp'][:10]}",
                "sk": results['timestamp'],
                "symbols_processed": results['symbols_processed'],
                "trades_executed": results['trades_executed'],
                "errors": results['errors'],
                "processing_time": str(results['total_processing_time'])
            })
            
            # Store individual trade results
            for symbol, result in results['results'].items():
                if result.get('trade_result', {}).get('success'):
                    trade = result['trade_result']
                    table.put_item(Item={
                        "pk": f"TRADE#{symbol}",
                        "sk": results['timestamp'],
                        "symbol": symbol,
                        "direction": trade['direction'],
                        "entry_price": str(trade['entry_price']),
                        "stop_loss": str(trade['stop_loss']),
                        "take_profit": str(trade['take_profit']),
                        "lot_size": str(trade['lot_size']),
                        "regime": result['analysis']['regime'],
                        "reasoning": result['analysis']['decision_reasoning'][:500]
                    })
                    
        except Exception as e:
            print(f"Failed to store results in DynamoDB: {e}")


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler - main entry point.
    
    Event can contain:
    - symbols: List of symbols to process (optional)
    - timeframe: Timeframe to use (optional, default H1)
    - dry_run: Whether to execute real trades (optional, default True)
    
    Returns:
        Dict with processing results
    """
    print(f"Kuiper V2 Lambda invoked at {datetime.now(timezone.utc).isoformat()}")
    
    # Parse event
    symbols = event.get("symbols", SYMBOLS)
    timeframe = event.get("timeframe", DEFAULT_TIMEFRAME)
    dry_run = event.get("dry_run", os.environ.get("DRY_RUN", "true").lower() == "true")
    account_balance = float(event.get("account_balance", os.environ.get("ACCOUNT_BALANCE", "10000")))
    
    print(f"Processing {len(symbols)} symbols on {timeframe}")
    print(f"Dry run: {dry_run}")
    
    # Initialize engine
    engine = KuiperEngine(dry_run=dry_run, account_balance=account_balance)
    
    # Process all symbols
    results = engine.process_all_symbols(
        symbols=symbols,
        timeframe=timeframe,
        parallel=True
    )
    
    # Log summary
    print(f"Processed {results['symbols_processed']} symbols in {results['total_processing_time']:.2f}s")
    print(f"Trades executed: {results['trades_executed']}")
    print(f"Errors: {results['errors']}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Kuiper V2 execution complete",
            "symbols_processed": results['symbols_processed'],
            "trades_executed": results['trades_executed'],
            "errors": results['errors'],
            "processing_time": results['total_processing_time']
        })
    }


# =============================================================================
# LOCAL TESTING
# =============================================================================

if __name__ == "__main__":
    # Test locally
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load credentials
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "env.json")
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8-sig') as f:
            env = json.load(f)
            if "Variables" in env:
                env = env["Variables"]
            os.environ["METAAPI_TOKEN"] = env.get("METAAPI_TOKEN", "")
            os.environ["METAAPI_ACCOUNT_ID"] = env.get("METAAPI_ACCOUNT_ID", "")
    
    # Run test
    result = handler({
        "symbols": ["EURUSD"],
        "timeframe": "H1",
        "dry_run": True
    }, None)
    
    print(json.dumps(result, indent=2))
