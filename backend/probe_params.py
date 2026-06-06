#!/usr/bin/env python3
"""Probe RealEstateAPI base URL with different query parameter names (zip/postal/etc.).
"""
import os
import requests

ENV = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(ENV):
    with open(ENV) as f:
        for l in f:
            if '=' in l and not l.strip().startswith('#'):
                k, v = l.strip().split('=', 1)
                os.environ.setdefault(k, v)

API_KEY = os.getenv('REAL_ESTATE_API_KEY')
BASE = os.getenv('REAL_ESTATE_API_URL', 'https://api.realestateapi.com/v1/market')
ZIPS = ['90210','10001','94105']
PARAM_NAMES = ['zip','zipcode','zip_code','postal_code','postalcode','postal','code','q']

def test():
    if not API_KEY:
        print('No REAL_ESTATE_API_KEY')
        return
    print('Base:', BASE)
    for z in ZIPS:
        print('\nZIP', z)
        for p in PARAM_NAMES:
            url = BASE
            try:
                r = requests.get(url, params={p: z, 'apikey': API_KEY}, timeout=6)
                print(f'  param {p}: {r.status_code}')
                if r.status_code == 200:
                    print('   body:', r.text[:300])
                    return
            except Exception as e:
                print('  err', e)

if __name__ == '__main__':
    test()
