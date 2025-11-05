"""Quick test for price API integration."""

from agents.price_service import get_price_service


def test_price_apis():
    """Test both Metal Price API and Forex Rate API."""
    print("=" * 60)
    print("TESTING PRICE APIS")
    print("=" * 60)

    price_service = get_price_service()

    # Test commodity (Metal Price API)
    print("\n1️⃣  Testing Metal Price API (XAU/USD)...")
    gold_price = price_service.get_price("XAU/USD")

    if gold_price:
        print(f"   ✅ Success!")
        print(f"   Price: ${gold_price['price']}")
        print(f"   Source: {gold_price['source']}")
    else:
        print(f"   ❌ Failed to fetch gold price")

    # Test forex (Forex Rate API)
    print("\n2️⃣  Testing Forex Rate API (EUR/USD)...")
    eur_price = price_service.get_price("EUR/USD")

    if eur_price:
        print(f"   ✅ Success!")
        print(f"   Price: ${eur_price['price']}")
        print(f"   Source: {eur_price['source']}")
    else:
        print(f"   ❌ Failed to fetch EUR/USD price")

    # Summary
    print("\n" + "=" * 60)
    if gold_price and eur_price:
        print("✅ BOTH APIs WORKING!")
        print("\nYou can now use real-time prices in the system.")
        return 0
    else:
        print("⚠️  ONE OR MORE APIs FAILED")
        print("\nThe system will fall back to mock prices.")
        print("Check your API keys in .env file.")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(test_price_apis())
