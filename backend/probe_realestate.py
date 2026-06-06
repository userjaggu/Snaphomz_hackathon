#!/usr/bin/env python3
"""Simple probe script to check which ZIP codes are supported by the configured RealEstateAPI.

Usage:
  REAL_ESTATE_API_KEY=your_key_here python3 probe_realestate.py

The script will print HTTP status codes and any JSON payload returned.
"""
import os
import sys
import time
import json
import requests

API_KEY = os.getenv("REAL_ESTATE_API_KEY")
API_URL = os.getenv("REAL_ESTATE_API_URL", "https://api.realestateapi.com/v1/market")

CANDIDATE_ZIPS = ["90210", "10001", "94105", "33139", "60611", "02139", "30301", "77002", "98101", "15213"]

def main():
    if not API_KEY:
        print("REAL_ESTATE_API_KEY not set. Please export REAL_ESTATE_API_KEY and rerun.")
        sys.exit(1)

    print(f"Using API URL: {API_URL}")
    print(f"Probing {len(CANDIDATE_ZIPS)} ZIPs...\n")

    for z in CANDIDATE_ZIPS:
        url = f"{API_URL}/{z}"
        try:
            resp = requests.get(url, params={"apikey": API_KEY}, timeout=8)
            print(f"{z}: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    payload = resp.json()
                    print(json.dumps(payload, indent=2)[:1000])
                except Exception:
                    print(resp.text[:500])
        except Exception as e:
            print(f"{z}: error {e}")
        time.sleep(0.2)

if __name__ == '__main__':
    main()
