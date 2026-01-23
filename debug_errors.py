"""Debug the failing pairs"""
import json
import sys
import os
sys.path.insert(0, '.')

env_path = '../env.json'
for encoding in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
    try:
        with open(env_path, encoding=encoding) as f:
            env = json.load(f)
        break
    except:
        continue

if 'Variables' in env:
    env = env['Variables']
os.environ['METAAPI_TOKEN'] = env.get('METAAPI_TOKEN', '')
os.environ['METAAPI_ACCOUNT_ID'] = env.get('METAAPI_ACCOUNT_ID', '')

from src.handler import KuiperEngine
engine = KuiperEngine(dry_run=True)

for symbol in ['GBPUSD', 'GBPJPY', 'EURGBP']:
    print(f'Testing {symbol}...')
    result = engine.process_symbol(symbol, 'H1')
    if not result['success']:
        err = result.get('error', 'Unknown')
        print(f'  ERROR: {err}')
    else:
        regime = result['analysis']['regime']
        decision = result['analysis']['decision']
        print(f'  OK: {regime} -> {decision}')
