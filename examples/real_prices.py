"""Real-time price integration examples."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.price_service import get_price_service, PriceService
from agents.technical_agent import TechnicalAgent
from system import ForexAgentSystem


def example_1_fetch_prices():
    """Example 1: Fetch real-time prices directly."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Fetching Real-Time Prices")
    print("=" * 70)

    price_service = get_price_service()

    # Test various asset types
    pairs = [
        "XAU/USD",  # Gold (commodity)
        "XAG/USD",  # Silver (commodity)
        "EUR/USD",  # Forex
        "BTC/USD",  # Crypto
        "GBP/USD",  # Forex
    ]

    print("\nFetching prices for multiple assets...\n")

    for pair in pairs:
        price_data = price_service.get_price(pair)

        if price_data:
            print(f"✅ {pair}")
            print(f"   Price: ${price_data['price']}")
            print(f"   Bid: ${price_data['bid']} | Ask: ${price_data['ask']}")
            print(f"   Source: {price_data['source']}")
            print(f"   Timestamp: {price_data['timestamp']}")
        else:
            print(f"❌ {pair} - Failed to fetch price")

        print()


def example_2_technical_agent_real_prices():
    """Example 2: Technical agent with real prices."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Technical Agent with Real Prices")
    print("=" * 70)

    # Create agent with real prices enabled
    agent = TechnicalAgent(use_real_prices=True)

    print("\nAnalyzing XAU/USD (Gold) with real price data...\n")

    result = agent.analyze("XAU/USD")

    if result["success"]:
        data = result["data"]
        print(f"✅ Analysis Complete")
        print(f"   Pair: {data['pair']}")
        print(f"   Current Price: ${data['current_price']}")
        print(f"   Price Source: {data['price_source']}")
        print(f"   Trend: {data['trend']}")
        print(f"   RSI: {data['indicators']['rsi']}")
        print(f"   Signal: {data['signals']['overall']}")
        print(f"\n   Summary: {data['summary']}")


def example_3_compare_real_vs_mock():
    """Example 3: Compare real vs mock prices."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Real vs Mock Price Comparison")
    print("=" * 70)

    pair = "EUR/USD"

    # Real prices
    print(f"\n📊 Analyzing {pair} with REAL prices:")
    agent_real = TechnicalAgent(use_real_prices=True)
    result_real = agent_real.analyze(pair)

    if result_real["success"]:
        print(f"   Price: ${result_real['data']['current_price']}")
        print(f"   Source: {result_real['data']['price_source']}")

    # Mock prices
    print(f"\n📊 Analyzing {pair} with MOCK prices:")
    agent_mock = TechnicalAgent(use_real_prices=False)
    result_mock = agent_mock.analyze(pair)

    if result_mock["success"]:
        print(f"   Price: ${result_mock['data']['current_price']}")
        print(f"   Source: {result_mock['data']['price_source']}")

    # Compare
    if result_real["success"] and result_mock["success"]:
        real_price = result_real["data"]["current_price"]
        mock_price = result_mock["data"]["current_price"]
        diff_pct = abs(real_price - mock_price) / real_price * 100

        print(f"\n💡 Comparison:")
        print(f"   Real Price: ${real_price}")
        print(f"   Mock Price: ${mock_price}")
        print(f"   Difference: {diff_pct:.2f}%")


def example_4_full_system_real_prices():
    """Example 4: Full system with real prices."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Full System Analysis with Real Prices")
    print("=" * 70)

    system = ForexAgentSystem()

    # Analyze gold with natural language
    print("\n🔍 Query: 'Analyze gold trading'\n")
    result = system.analyze("Analyze gold trading", verbose=False)

    # Check if real prices were used
    tech_data = result["agent_results"]["technical"]["data"]

    print(f"\n✅ Analysis Complete")
    print(f"   Parsed Pair: {result['query_context']['pair']}")
    print(f"   Asset Type: {result['query_context']['asset_type']}")
    print(f"   Current Price: ${tech_data['current_price']}")
    print(f"   Price Source: {tech_data['price_source']}")
    print(f"   Decision: {result['decision']['action']}")
    print(f"   Confidence: {result['decision']['confidence']:.0%}")


def example_5_cache_performance():
    """Example 5: Demonstrate price caching."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Price Caching Performance")
    print("=" * 70)

    import time

    price_service = get_price_service()
    pair = "XAU/USD"

    # First fetch (uncached)
    print(f"\n1️⃣  First fetch (uncached):")
    start = time.time()
    price1 = price_service.get_price(pair)
    elapsed1 = time.time() - start
    print(f"   Time: {elapsed1*1000:.0f}ms")
    if price1:
        print(f"   Price: ${price1['price']}")

    # Second fetch (cached)
    print(f"\n2️⃣  Second fetch (from cache):")
    start = time.time()
    price2 = price_service.get_price(pair)
    elapsed2 = time.time() - start
    print(f"   Time: {elapsed2*1000:.0f}ms")
    if price2:
        print(f"   Price: ${price2['price']}")

    # Performance comparison
    speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 0
    print(f"\n💡 Cache Performance:")
    print(f"   Speedup: {speedup:.0f}x faster")
    print(f"   Cache saves: {(elapsed1-elapsed2)*1000:.0f}ms per request")

    # Show cache info
    cache_info = price_service.get_cache_info()
    print(f"\n📦 Cache Status:")
    print(f"   Cached pairs: {cache_info['cached_pairs']}")
    print(f"   Cache size: {cache_info['cache_size']}")


def example_6_multiple_assets():
    """Example 6: Analyze multiple assets with real prices."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Multi-Asset Analysis")
    print("=" * 70)

    system = ForexAgentSystem()

    queries = [
        "Analyze gold trading",  # XAU/USD
        "What about EUR/USD?",  # EUR/USD
        "Should I buy Bitcoin?",  # BTC/USD
    ]

    print("\nAnalyzing multiple assets...\n")

    results = []
    for query in queries:
        print(f"🔍 {query}")
        result = system.analyze(query, verbose=False)

        pair = result["query_context"]["pair"]
        tech_data = result["agent_results"]["technical"]["data"]
        price = tech_data["current_price"]
        source = tech_data["price_source"]
        decision = result["decision"]["action"]

        print(f"   Pair: {pair}")
        print(f"   Price: ${price} ({source})")
        print(f"   Decision: {decision}")
        print()

        results.append(result)

    print(f"✅ Analyzed {len(results)} assets with real-time prices!")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("REAL-TIME PRICE INTEGRATION EXAMPLES")
    print("=" * 70)

    try:
        example_1_fetch_prices()
        example_2_technical_agent_real_prices()
        example_3_compare_real_vs_mock()
        example_4_full_system_real_prices()
        example_5_cache_performance()
        example_6_multiple_assets()

        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED!")
        print("=" * 70)

        print("\n💡 Key Features Demonstrated:")
        print("   ✓ Real-time price fetching from external APIs")
        print("   ✓ Support for commodities, forex, and crypto")
        print("   ✓ Automatic API selection based on asset type")
        print("   ✓ Price caching for performance")
        print("   ✓ Graceful fallback to mock data")
        print("   ✓ Integration with full trading system")

        print("\n📊 APIs Used:")
        print("   • Metal Price API: https://metalpriceapi.com")
        print("   • Forex Rate API: https://forexrateapi.com")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
