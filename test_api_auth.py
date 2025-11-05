"""Test API authentication methods to verify no 40x errors."""

import os
import requests

METAL_API_KEY = os.getenv("METAL_PRICE_API_KEY", "d6f328d4c0d57e82aa2202840197ba1c")
FOREX_API_KEY = os.getenv("FOREX_RATE_API_KEY", "f15a3cce2b1df6bf25fc31fe69e9afc4")


def test_metal_api_query_param():
    """Test Metal Price API with query parameter authentication."""
    print("\n" + "=" * 70)
    print("TEST 1: Metal Price API - Query Parameter Authentication")
    print("=" * 70)

    url = "https://api.metalpriceapi.com/v1/latest"
    params = {
        "api_key": METAL_API_KEY,
        "base": "USD",
        "currencies": "XAU"
    }

    print(f"\nRequest: GET {url}")
    print(f"Params: base=USD, currencies=XAU")
    print(f"Auth: Query parameter (?api_key=...)")

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                rate = data.get("rates", {}).get("XAU")
                if rate:
                    price = 1.0 / rate
                    print(f"✅ SUCCESS!")
                    print(f"   XAU/USD Price: ${price:,.2f}")
                    print(f"   Raw Rate: {rate}")
                    return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_metal_api_header():
    """Test Metal Price API with header authentication."""
    print("\n" + "=" * 70)
    print("TEST 2: Metal Price API - Header Authentication (X-API-KEY)")
    print("=" * 70)

    url = "https://api.metalpriceapi.com/v1/latest"
    params = {
        "base": "USD",
        "currencies": "XAU"
    }
    headers = {
        "X-API-KEY": METAL_API_KEY,
        "Content-Type": "application/json"
    }

    print(f"\nRequest: GET {url}")
    print(f"Params: base=USD, currencies=XAU")
    print(f"Auth: Header (X-API-KEY)")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                rate = data.get("rates", {}).get("XAU")
                if rate:
                    price = 1.0 / rate
                    print(f"✅ SUCCESS!")
                    print(f"   XAU/USD Price: ${price:,.2f}")
                    print(f"   Raw Rate: {rate}")
                    return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_forex_api_query_param():
    """Test Forex Rate API with query parameter authentication."""
    print("\n" + "=" * 70)
    print("TEST 3: Forex Rate API - Query Parameter Authentication")
    print("=" * 70)

    url = "https://api.forexrateapi.com/v1/latest"
    params = {
        "api_key": FOREX_API_KEY,
        "base": "EUR",
        "currencies": "USD"
    }

    print(f"\nRequest: GET {url}")
    print(f"Params: base=EUR, currencies=USD")
    print(f"Auth: Query parameter (?api_key=...)")

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                rate = data.get("rates", {}).get("USD")
                if rate:
                    print(f"✅ SUCCESS!")
                    print(f"   EUR/USD Rate: {rate:.5f}")
                    return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_forex_api_header():
    """Test Forex Rate API with header authentication."""
    print("\n" + "=" * 70)
    print("TEST 4: Forex Rate API - Header Authentication (X-API-KEY)")
    print("=" * 70)

    url = "https://api.forexrateapi.com/v1/latest"
    params = {
        "base": "EUR",
        "currencies": "USD"
    }
    headers = {
        "X-API-KEY": FOREX_API_KEY,
        "Content-Type": "application/json"
    }

    print(f"\nRequest: GET {url}")
    print(f"Params: base=EUR, currencies=USD")
    print(f"Auth: Header (X-API-KEY)")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                rate = data.get("rates", {}).get("USD")
                if rate:
                    print(f"✅ SUCCESS!")
                    print(f"   EUR/USD Rate: {rate:.5f}")
                    return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def main():
    """Run all authentication tests."""
    print("\n" + "=" * 70)
    print("API AUTHENTICATION VERIFICATION TEST")
    print("Testing both query parameter and header authentication methods")
    print("=" * 70)

    print(f"\nUsing API Keys:")
    print(f"  Metal Price API: {METAL_API_KEY[:8]}...{METAL_API_KEY[-4:]}")
    print(f"  Forex Rate API:  {FOREX_API_KEY[:8]}...{FOREX_API_KEY[-4:]}")

    results = {}

    # Test Metal Price API
    results["metal_query"] = test_metal_api_query_param()
    results["metal_header"] = test_metal_api_header()

    # Test Forex Rate API
    results["forex_query"] = test_forex_api_query_param()
    results["forex_header"] = test_forex_api_header()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\n📊 Metal Price API:")
    print(f"   Query Parameter: {'✅ PASS' if results['metal_query'] else '❌ FAIL'}")
    print(f"   Header (X-API-KEY): {'✅ PASS' if results['metal_header'] else '❌ FAIL'}")

    print("\n📊 Forex Rate API:")
    print(f"   Query Parameter: {'✅ PASS' if results['forex_query'] else '❌ FAIL'}")
    print(f"   Header (X-API-KEY): {'✅ PASS' if results['forex_header'] else '❌ FAIL'}")

    # Recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    all_passed = all(results.values())
    if all_passed:
        print("\n✅ All authentication methods work!")
        print("   Both query parameter and header authentication are functional.")
        print("   Current implementation using query parameters is fine.")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n⚠️  Some tests failed: {', '.join(failed)}")
        print("   Consider checking API keys or rate limits.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
