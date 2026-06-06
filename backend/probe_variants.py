#!/usr/bin/env python3
"""Probe RealEstateAPI with multiple endpoint and auth variants to find a working pattern.
Reads backend/.env if present to load keys for convenience (doesn't print keys).
"""
import os
import requests
import time

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k, v)

API_KEY = os.getenv('REAL_ESTATE_API_KEY')
API_URL = os.getenv('REAL_ESTATE_API_URL', 'https://api.realestateapi.com/v1/market')

ZIPS = ["90210","10001","94105","33139","60611","02139","30301"]

ENDPOINT_PATTERNS = [
    '{base}/{zip}',
    '{base}?zip={zip}',
    '{base}/search/{zip}',
    '{base}/search?zip={zip}',
    '{base}/v1/market/{zip}',
]

AUTH_VARIANTS = [
    ('param_apikey', None),
    ('header_x_api_key', None),
    ('header_bearer', None),
]

def try_request(url, headers, params):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=7)
        return r.status_code, r.text[:1000]
    except Exception as e:
        return None, str(e)

def main():
    if not API_KEY:
        print('REAL_ESTATE_API_KEY not set in environment or backend/.env. Aborting.')
        return

    print('API base:', API_URL)
    print('Probing variants...')

    for z in ZIPS:
        print('\nZIP:', z)
        for pattern in ENDPOINT_PATTERNS:
            url = pattern.format(base=API_URL.rstrip('/'), zip=z)
            # try param apikey
            code, body = try_request(url, headers={}, params={'apikey': API_KEY})
            print(f'  PATTERN param_apikey -> {url}  STATUS: {code}')
            if code == 200:
                print('    SUCCESS body:', body[:300])
                return

            # try x-api-key header
            code, body = try_request(url, headers={'x-api-key': API_KEY}, params={})
            print(f'  PATTERN x-api-key -> STATUS: {code}')
            if code == 200:
                print('    SUCCESS body:', body[:300])
                return

            # try Authorization: Bearer
            code, body = try_request(url, headers={'Authorization': f'Bearer {API_KEY}'}, params={})
            print(f'  PATTERN bearer -> STATUS: {code}')
            if code == 200:
                print('    SUCCESS body:', body[:300])
                return

            time.sleep(0.1)

    print('\nNo working pattern found. Check provider docs or contact support.')

if __name__ == '__main__':
    main()
