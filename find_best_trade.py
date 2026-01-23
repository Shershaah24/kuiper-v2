"""
Find Best Trade - Kuiper V2
===========================
Analyzes 10 forex pairs and selects the BEST trade opportunity
based on indicator agreement, regime clarity, and risk/reward.
"""

import json
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load credentials
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "env.json")
for encoding in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
    try:
        with open(env_path, encoding=encoding) as f:
            env = json.load(f)
        break
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue

if "Variables" in env:
    env = env["Variables"]

os.environ["METAAPI_TOKEN"] = env.get("METAAPI_TOKEN", "")
os.environ["METAAPI_ACCOUNT_ID"] = env.get("METAAPI_ACCOUNT_ID", "")

from src.handler import KuiperEngine


def calculate_trade_score(result):
    """Calculate a quality score for each trade opportunity."""
    if not result.get('success') or not result.get('analysis'):
        return -1  # Return -1 for errors (different from 0 for NO_TRADE)
    
    analysis = result['analysis']
    
    # NO_TRADE decisions get 0 score
    decision = analysis.get('decision', 'NO_TRADE')
    if decision == 'NO_TRADE':
        return 0
    
    score = 0
    
    # 1. Regime clarity (trending is better than ranging)
    regime = analysis.get('regime', '')
    if 'TRENDING' in regime:
        score += 30  # Strong trend = better opportunity
    elif regime == 'RANGING':
        score += 10  # Ranging = less clear
    elif regime == 'VOLATILE':
        score += 5   # Volatile = risky
    
    # 2. Position size (higher = more confidence)
    pos_size = analysis.get('position_size_multiplier', 0)
    score += pos_size * 25  # Max 25 points for 100% position
    
    # 3. Risk/Reward ratio
    rr = analysis.get('risk_reward_ratio', 0)
    if rr >= 2.0:
        score += 20
    elif rr >= 1.5:
        score += 15
    elif rr >= 1.0:
        score += 10
    
    # 4. Confidence factors count
    conf_factors = len(analysis.get('confidence_factors', []))
    score += conf_factors * 5  # 5 points per confidence factor
    
    # 5. Warning factors penalty
    warn_factors = len(analysis.get('warning_factors', []))
    score -= warn_factors * 10  # -10 points per warning
    
    # 6. Decision clarity bonus
    score += 10  # Already has LONG/SHORT decision
    
    return max(0, score)


def find_best_trade():
    """Analyze 10 pairs and find the best trade opportunity."""
    print("=" * 70)
    print("KUIPER V2 - FINDING BEST TRADE FROM 10 PAIRS")
    print("=" * 70)
    
    # 10 major forex pairs
    symbols = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
        "USDCHF", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"
    ]
    
    print(f"\nAnalyzing {len(symbols)} pairs...")
    print("-" * 70)
    
    # Initialize engine
    engine = KuiperEngine(dry_run=True, account_balance=10000.0)
    
    # Process all symbols
    start = time.time()
    results = engine.process_all_symbols(symbols=symbols, parallel=True)
    elapsed = time.time() - start
    
    print(f"Analysis complete in {elapsed:.2f} seconds\n")
    
    # Score each trade
    scored_trades = []
    for symbol, result in results['results'].items():
        score = calculate_trade_score(result)
        scored_trades.append({
            'symbol': symbol,
            'score': score,
            'result': result
        })
    
    # Sort by score (highest first)
    scored_trades.sort(key=lambda x: x['score'], reverse=True)
    
    # Display rankings
    print("=" * 70)
    print("TRADE RANKINGS (Best to Worst)")
    print("=" * 70)
    print(f"{'Rank':<6}{'Symbol':<10}{'Score':<8}{'Regime':<15}{'Decision':<10}{'Size':<8}{'R:R':<6}")
    print("-" * 70)
    
    for i, trade in enumerate(scored_trades, 1):
        result = trade['result']
        score = trade['score']
        
        if score == -1:
            # Error/timeout
            regime = 'TIMEOUT'
            decision = 'N/A'
            size = 'N/A'
            rr = 'N/A'
            err = result.get('error', 'Unknown')[:30]
            score_str = f"ERR"
        elif result.get('success') and result.get('analysis'):
            analysis = result['analysis']
            regime = analysis.get('regime', 'N/A')
            decision = analysis.get('decision', 'N/A')
            size = f"{analysis.get('position_size_multiplier', 0) * 100:.0f}%"
            rr = f"{analysis.get('risk_reward_ratio', 0):.2f}"
            score_str = str(score)
        else:
            regime = 'ERROR'
            decision = 'N/A'
            size = 'N/A'
            rr = 'N/A'
            score_str = "0"
        
        marker = "🏆" if i == 1 and score > 0 else "  "
        print(f"{marker}{i:<4}{trade['symbol']:<10}{score_str:<8}{regime:<15}{decision:<10}{size:<8}{rr:<6}")
    
    # Show the BEST trade details
    best = scored_trades[0]
    print("\n" + "=" * 70)
    print(f"🏆 BEST TRADE: {best['symbol']}")
    print("=" * 70)
    
    if best['result'].get('success') and best['result'].get('analysis'):
        analysis = best['result']['analysis']
        trade_result = best['result'].get('trade_result', {})
        
        print(f"\nREGIME: {analysis['regime']}")
        print(f"DECISION: {analysis['decision']}")
        print(f"POSITION SIZE: {analysis['position_size_multiplier'] * 100:.0f}%")
        print(f"QUALITY SCORE: {best['score']}/100")
        
        print(f"\nTRADE PARAMETERS:")
        print(f"  Entry: {analysis.get('entry_price', 'N/A')}")
        print(f"  Stop Loss: {analysis.get('stop_loss', 'N/A')}")
        print(f"  Take Profit: {analysis.get('take_profit', 'N/A')}")
        print(f"  Risk/Reward: {analysis.get('risk_reward_ratio', 'N/A')}")
        
        if trade_result:
            print(f"  Lot Size: {trade_result.get('lot_size', 'N/A')}")
        
        print(f"\nCONFIDENCE FACTORS:")
        for factor in analysis.get('confidence_factors', []):
            print(f"  ✓ {factor}")
        
        if analysis.get('warning_factors'):
            print(f"\nWARNING FACTORS:")
            for warning in analysis['warning_factors']:
                print(f"  ⚠ {warning}")
        
        print(f"\n{'-' * 70}")
        print("FULL ANALYSIS:")
        print(analysis.get('decision_reasoning', 'N/A')[:2000])
    
    # Save results
    output = {
        'timestamp': results['timestamp'],
        'best_trade': {
            'symbol': best['symbol'],
            'score': best['score'],
            'analysis': best['result'].get('analysis'),
            'trade_result': best['result'].get('trade_result')
        },
        'all_rankings': [
            {
                'rank': i+1,
                'symbol': t['symbol'],
                'score': t['score'],
                'regime': t['result'].get('analysis', {}).get('regime', 'N/A'),
                'decision': t['result'].get('analysis', {}).get('decision', 'N/A')
            }
            for i, t in enumerate(scored_trades)
        ]
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best_trade.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n{'=' * 70}")
    print(f"Results saved to: {output_path}")
    print("=" * 70)
    
    return output


if __name__ == "__main__":
    find_best_trade()
