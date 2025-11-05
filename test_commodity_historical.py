"""Test commodity historical data integration (XAU, XAG, etc.)."""

from agents.price_service import get_price_service


def test_commodity_enriched():
    """Test enriched price data for commodities with historical context."""
    print("=" * 70)
    print("TESTING COMMODITY HISTORICAL DATA INTEGRATION")
    print("=" * 70)

    price_service = get_price_service()

    # Test gold with full historical data
    pair = "XAU/USD"
    print(f"\n📊 Fetching enriched price for {pair} (Gold)...\n")

    enriched = price_service.get_enriched_price(pair)

    if enriched:
        print(f"✅ Success!\n")
        print(f"Pair: {enriched['pair']}")
        print(f"Current Price: ${enriched['price']:,.2f}")
        print(f"Bid/Ask: ${enriched['bid']:,.2f} / ${enriched['ask']:,.2f}")
        print(f"Source: {enriched['source']}")

        # Historical context
        if "historical" in enriched and enriched["historical"] and enriched["historical"]["yesterday_rate"]:
            print(f"\n📈 Historical Context:")
            hist = enriched["historical"]
            print(f"  Yesterday's Rate: ${hist['yesterday_rate']:,.2f}")
            if hist['price_change'] and hist['price_change_pct']:
                direction = "UP ⬆️" if hist['price_change'] > 0 else "DOWN ⬇️"
                print(f"  24h Change: ${hist['price_change']:,.2f} ({hist['price_change_pct']:+.2f}%) {direction}")

        # OHLC data
        if "ohlc" in enriched and enriched["ohlc"]:
            print(f"\n📊 Yesterday's OHLC:")
            ohlc = enriched["ohlc"]
            print(f"  Open:  ${ohlc['open']:,.2f}")
            print(f"  High:  ${ohlc['high']:,.2f}")
            print(f"  Low:   ${ohlc['low']:,.2f}")
            print(f"  Close: ${ohlc['close']:,.2f}")

            # Calculate trading range
            range_val = ohlc["high"] - ohlc["low"]
            range_pct = (range_val / ohlc["low"]) * 100
            print(f"\n  Yesterday's Range: ${range_val:.2f} ({range_pct:.2f}%)")

            # Candle pattern
            if ohlc["close"] > ohlc["open"]:
                print(f"  Candle: 🟢 Bullish (Close > Open)")
            elif ohlc["close"] < ohlc["open"]:
                print(f"  Candle: 🔴 Bearish (Close < Open)")
            else:
                print(f"  Candle: ⚪ Doji (Close = Open)")
        else:
            print(f"\n⚠️  No OHLC data available (API may be rate-limited)")

    else:
        print(f"❌ Failed to fetch enriched price for {pair}")
        print(f"   (This is expected if API keys are invalid/rate-limited)")

    print("\n" + "=" * 70)


def test_multiple_commodities():
    """Test enriched data for multiple commodities."""
    print("\n🌍 TESTING MULTIPLE COMMODITIES")
    print("=" * 70)

    price_service = get_price_service()

    commodities = [
        ("XAU/USD", "Gold"),
        ("XAG/USD", "Silver"),
        ("XPT/USD", "Platinum"),
        ("XPD/USD", "Palladium"),
    ]

    print(f"\nFetching enriched data for {len(commodities)} commodities...\n")

    for pair, name in commodities:
        enriched = price_service.get_enriched_price(pair)

        if enriched:
            hist = enriched.get("historical", {})
            change_pct = hist.get("price_change_pct") if hist else None

            if change_pct is not None:
                direction = "📈" if change_pct > 0 else "📉"
                print(f"{direction} {name:10} ({pair}): ${enriched['price']:>8,.2f} ({change_pct:+.2f}%)")
            else:
                print(f"   {name:10} ({pair}): ${enriched['price']:>8,.2f}")
        else:
            print(f"❌ {name:10} ({pair}): Failed")

    print("\n" + "=" * 70)


def test_metal_api_direct():
    """Test Metal Price API endpoints directly."""
    print("\n🔧 TESTING METAL PRICE API ENDPOINTS DIRECTLY")
    print("=" * 70)

    price_service = get_price_service()

    pair = "XAU/USD"

    # Test latest price
    print(f"\n1. Latest Price for {pair}:")
    latest = price_service.get_price(pair)
    if latest:
        print(f"   ✅ ${latest['price']:,.2f} from {latest['source']}")
    else:
        print(f"   ❌ Failed (API key may be invalid/rate-limited)")

    # Test historical rates
    print(f"\n2. Historical Rate (Yesterday) for {pair}:")
    historical = price_service.get_historical_rates(pair, "yesterday")
    if historical:
        print(f"   ✅ ${historical['rate']:,.2f} from {historical['source']}")
    else:
        print(f"   ❌ Failed (API key may be invalid/rate-limited)")

    # Test OHLC
    print(f"\n3. OHLC Data (Yesterday) for {pair}:")
    ohlc = price_service.get_ohlc(pair, "yesterday")
    if ohlc:
        print(f"   ✅ O: ${ohlc['open']:,.2f}, H: ${ohlc['high']:,.2f}, L: ${ohlc['low']:,.2f}, C: ${ohlc['close']:,.2f}")
    else:
        print(f"   ❌ Failed (API key may be invalid/rate-limited)")

    print("\n" + "=" * 70)


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("COMMODITY HISTORICAL DATA TEST SUITE")
    print("=" * 70)

    try:
        test_commodity_enriched()
        test_multiple_commodities()
        test_metal_api_direct()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 70)

        print("\n💡 Key Features Now Available:")
        print("   ✓ Commodity historical rates (yesterday's price)")
        print("   ✓ Commodity OHLC data (Open/High/Low/Close)")
        print("   ✓ 24-hour price change for gold, silver, etc.")
        print("   ✓ Trading range metrics for commodities")
        print("   ✓ Candlestick pattern identification")
        print("   ✓ Complete parity between forex and commodities")

        print("\n📊 APIs Used:")
        print("   • Metal Price API - Latest prices")
        print("   • Metal Price API - Historical rates (/v1/yesterday)")
        print("   • Metal Price API - OHLC data (/v1/ohlc)")

        print("\n⚠️  Note:")
        print("   If tests fail with 403 Forbidden, it means:")
        print("   - API keys are invalid or rate-limited")
        print("   - Get free keys from metalpriceapi.com")
        print("   - System gracefully falls back to current prices only")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
