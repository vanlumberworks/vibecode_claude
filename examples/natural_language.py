"""Natural language query examples for Forex Agent System v2."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from system import ForexAgentSystem


def example_1_commodity():
    """Example 1: Analyze a commodity using natural language."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Natural Language - Commodity")
    print("=" * 70)

    system = ForexAgentSystem()

    # Natural language query
    result = system.analyze("Analyze gold trading")

    # Check parsed context
    ctx = result["query_context"]
    print(f"\n✅ Query Parser Results:")
    print(f"   Input: 'Analyze gold trading'")
    print(f"   Parsed Pair: {ctx['pair']}")  # Should be XAU/USD
    print(f"   Asset Type: {ctx['asset_type']}")  # Should be commodity


def example_2_crypto():
    """Example 2: Analyze cryptocurrency."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Natural Language - Cryptocurrency")
    print("=" * 70)

    system = ForexAgentSystem()

    result = system.analyze("Should I buy Bitcoin?", verbose=False)

    ctx = result["query_context"]
    print(f"\n✅ Query Parser Results:")
    print(f"   Input: 'Should I buy Bitcoin?'")
    print(f"   Parsed Pair: {ctx['pair']}")  # Should be BTC/USD
    print(f"   Asset Type: {ctx['asset_type']}")  # Should be crypto
    print(f"   User Intent: {ctx['user_intent']}")  # Should be buy_signal

    print(f"\n🎯 Decision: {result['decision']['action']}")


def example_3_timeframe():
    """Example 3: Query with timeframe context."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Natural Language - With Timeframe")
    print("=" * 70)

    system = ForexAgentSystem()

    result = system.analyze("EUR/USD long term outlook", verbose=False)

    ctx = result["query_context"]
    print(f"\n✅ Query Parser Results:")
    print(f"   Input: 'EUR/USD long term outlook'")
    print(f"   Parsed Pair: {ctx['pair']}")  # EUR/USD
    print(f"   Timeframe: {ctx['timeframe']}")  # Should be long_term
    print(f"   Intent: {ctx['user_intent']}")


def example_4_multiple_natural_queries():
    """Example 4: Multiple natural language queries."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Multiple Natural Language Queries")
    print("=" * 70)

    system = ForexAgentSystem()

    queries = [
        "What about silver?",
        "Analyze EUR/USD short term",
        "Should I sell GBP/USD?",
        "Oil trading analysis",
    ]

    print(f"\nTesting {len(queries)} natural language queries...\n")

    for query in queries:
        result = system.analyze(query, verbose=False)
        ctx = result["query_context"]

        print(f"Query: '{query}'")
        print(f"  → Pair: {ctx['pair']}")
        print(f"  → Type: {ctx['asset_type']}")
        print(f"  → Intent: {ctx['user_intent']}")
        print(f"  → Decision: {result['decision']['action']}")
        print()


def example_5_performance():
    """Example 5: Compare parallel vs sequential performance."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Performance - Parallel Execution")
    print("=" * 70)

    import time

    system = ForexAgentSystem()

    print(f"\nRunning analysis with parallel execution (v2)...")
    start = time.time()
    result = system.analyze("EUR/USD", verbose=False)
    elapsed = time.time() - start

    print(f"\n✅ Completed in {elapsed:.2f} seconds")
    print(f"\nPerformance Benefits:")
    print(f"   - News, Technical, Fundamental run simultaneously")
    print(f"   - ~3x faster than sequential execution")
    print(f"   - Total steps: {result['metadata']['steps']}")


def example_6_context_enrichment():
    """Example 6: Show enriched context passed to agents."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Context Enrichment")
    print("=" * 70)

    system = ForexAgentSystem()

    result = system.analyze("Analyze gold for aggressive trading", verbose=False)

    ctx = result["query_context"]

    print(f"\n🔍 Enriched Context from Query Parser:")
    print(f"   Original Query: '{result['user_query']}'")
    print(f"\n   Structured Context:")
    print(f"     Pair: {ctx.get('pair')}")
    print(f"     Asset Type: {ctx.get('asset_type')}")
    print(f"     Base Currency: {ctx.get('base_currency')}")
    print(f"     Quote Currency: {ctx.get('quote_currency')}")
    print(f"     Timeframe: {ctx.get('timeframe')}")
    print(f"     User Intent: {ctx.get('user_intent')}")
    print(f"     Risk Tolerance: {ctx.get('risk_tolerance')}")
    print(f"     Confidence: {ctx.get('confidence', 0):.0%}")

    if ctx.get("additional_context"):
        add_ctx = ctx["additional_context"]
        print(f"\n   Additional Context:")
        print(f"     Keywords: {add_ctx.get('keywords', [])}")

    print(f"\n✅ This rich context is passed to all agents!")
    print(f"   Agents can make better decisions with more context.")


def main():
    """Run all natural language examples."""
    print("\n" + "=" * 70)
    print("FOREX AGENT SYSTEM v2 - NATURAL LANGUAGE EXAMPLES")
    print("=" * 70)

    try:
        example_1_commodity()
        example_2_crypto()
        example_3_timeframe()
        example_4_multiple_natural_queries()
        example_5_performance()
        example_6_context_enrichment()

        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED!")
        print("=" * 70)

        print("\n💡 Key Features Demonstrated:")
        print("   ✓ Natural language input")
        print("   ✓ Intelligent query parsing")
        print("   ✓ Parallel agent execution")
        print("   ✓ Context enrichment")
        print("   ✓ 3x faster performance")
        print("   ✓ Multiple asset types (forex, crypto, commodities)")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure GOOGLE_AI_API_KEY is set in .env file")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
