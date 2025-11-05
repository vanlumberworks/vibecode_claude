"""Price Service - Fetches real-time prices from external APIs."""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time


class PriceService:
    """
    Fetches real-time prices from external APIs.

    Supported APIs:
    - Metal Price API (metalpriceapi.com) - Commodities (gold, silver, etc.)
    - Forex Rate API (forexrateapi.com) - Forex pairs and crypto

    Features:
    - Automatic API selection based on asset type
    - Price caching to avoid rate limits
    - Graceful error handling
    - Fallback to mock data
    """

    # API endpoints
    METAL_API_URL = "https://api.metalpriceapi.com/v1/latest"
    FOREX_API_URL = "https://api.forexrateapi.com/v1/latest"

    # Commodity symbols
    COMMODITIES = ["XAU", "XAG", "XPT", "XPD"]  # Gold, Silver, Platinum, Palladium

    # Cache duration (seconds)
    CACHE_DURATION = 60  # 1 minute

    def __init__(self):
        """Initialize price service with API keys."""
        self.metal_api_key = os.getenv("METAL_PRICE_API_KEY", "d6f328d4c0d57e82aa2202840197ba1c")
        self.forex_api_key = os.getenv("FOREX_RATE_API_KEY", "f15a3cce2b1df6bf25fc31fe69e9afc4")

        # Price cache
        self._cache = {}
        self._cache_timestamps = {}

    def get_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get current price for a trading pair.

        Args:
            pair: Trading pair (e.g., "EUR/USD", "XAU/USD", "BTC/USD")

        Returns:
            Dict with price data or None if failed:
            {
                "pair": "XAU/USD",
                "price": 2641.50,
                "bid": 2641.00,
                "ask": 2642.00,
                "timestamp": "2025-11-05T14:30:00",
                "source": "metalpriceapi"
            }
        """
        # Check cache first
        cached = self._get_from_cache(pair)
        if cached:
            return cached

        # Parse pair
        base, quote = self._parse_pair(pair)

        # Determine which API to use
        if base in self.COMMODITIES:
            price_data = self._fetch_metal_price(base, quote)
        else:
            price_data = self._fetch_forex_price(base, quote)

        # Cache the result
        if price_data:
            self._cache[pair] = price_data
            self._cache_timestamps[pair] = time.time()

        return price_data

    def _parse_pair(self, pair: str) -> tuple:
        """Parse trading pair into base and quote currencies."""
        if "/" in pair:
            base, quote = pair.split("/")
        else:
            # Assume format like "EURUSD"
            base = pair[:3]
            quote = pair[3:]

        return base.upper(), quote.upper()

    def _fetch_metal_price(self, base: str, quote: str) -> Optional[Dict[str, Any]]:
        """
        Fetch commodity price from Metal Price API.

        API Format: https://api.metalpriceapi.com/v1/latest?api_key=KEY&base=USD&currencies=XAU
        Response: {"success":true,"base":"USD","timestamp":1762300799,"rates":{"XAU":0.0002502133}}
        """
        try:
            # Metal API uses inverted quotes (USD per ounce)
            # We need to request with base=USD and currency=XAU to get USD/XAU
            # Then invert to get XAU/USD

            params = {"api_key": self.metal_api_key, "base": quote, "currencies": base}

            response = requests.get(self.METAL_API_URL, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            if not data.get("success"):
                print(f"  ⚠️  Metal Price API error: {data.get('error', 'Unknown error')}")
                return None

            # Get rate (this is quote/base, e.g., USD per XAU ounce)
            rates = data.get("rates", {})
            rate_key = base  # e.g., "XAU"

            if rate_key not in rates:
                print(f"  ⚠️  {base} not found in Metal Price API response")
                return None

            # Rate is USD per ounce of gold (e.g., 0.0002502133)
            # We need to invert to get XAU/USD (e.g., 3996.59)
            inverted_rate = rates[rate_key]
            price = 1.0 / inverted_rate if inverted_rate > 0 else 0

            # Calculate bid/ask spread (assume 0.1% spread)
            spread = price * 0.001
            bid = price - spread / 2
            ask = price + spread / 2

            return {
                "pair": f"{base}/{quote}",
                "price": round(price, 2),
                "bid": round(bid, 2),
                "ask": round(ask, 2),
                "timestamp": datetime.utcfromtimestamp(data.get("timestamp", time.time())).isoformat(),
                "source": "metalpriceapi",
                "raw_rate": inverted_rate,
            }

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Metal Price API request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"  ⚠️  Metal Price API error: {str(e)}")
            return None

    def _fetch_forex_price(self, base: str, quote: str) -> Optional[Dict[str, Any]]:
        """
        Fetch forex/crypto price from Forex Rate API.

        API Format: https://api.forexrateapi.com/v1/latest?api_key=KEY&base=USD&currencies=EUR,BTC
        Response: {"success":true,"base":"USD","timestamp":1762300799,"rates":{"EUR":0.8688948049}}
        """
        try:
            # If quote is the base, we need to swap
            # e.g., EUR/USD means we want USD in terms of EUR
            # So we request base=EUR, currencies=USD

            params = {"api_key": self.forex_api_key, "base": base, "currencies": quote}

            response = requests.get(self.FOREX_API_URL, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            if not data.get("success"):
                print(f"  ⚠️  Forex Rate API error: {data.get('error', 'Unknown error')}")
                return None

            # Get rate
            rates = data.get("rates", {})

            if quote not in rates:
                print(f"  ⚠️  {quote} not found in Forex Rate API response")
                return None

            price = rates[quote]

            # Calculate bid/ask spread (assume 0.02% spread for forex)
            spread = price * 0.0002
            bid = price - spread / 2
            ask = price + spread / 2

            return {
                "pair": f"{base}/{quote}",
                "price": round(price, 5),
                "bid": round(bid, 5),
                "ask": round(ask, 5),
                "timestamp": datetime.utcfromtimestamp(data.get("timestamp", time.time())).isoformat(),
                "source": "forexrateapi",
            }

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Forex Rate API request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"  ⚠️  Forex Rate API error: {str(e)}")
            return None

    def _get_from_cache(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get price from cache if still valid."""
        if pair not in self._cache:
            return None

        # Check if cache is still valid
        cache_age = time.time() - self._cache_timestamps.get(pair, 0)
        if cache_age > self.CACHE_DURATION:
            # Cache expired
            del self._cache[pair]
            del self._cache_timestamps[pair]
            return None

        return self._cache[pair]

    def clear_cache(self):
        """Clear price cache."""
        self._cache.clear()
        self._cache_timestamps.clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_pairs": list(self._cache.keys()),
            "cache_size": len(self._cache),
            "oldest_entry": min(self._cache_timestamps.values()) if self._cache_timestamps else None,
        }


# Singleton instance
_price_service = None


def get_price_service() -> PriceService:
    """Get singleton price service instance."""
    global _price_service
    if _price_service is None:
        _price_service = PriceService()
    return _price_service
