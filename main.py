"""Main entry point for Forex Agent System."""

import sys
from system import ForexAgentSystem


def main():
    """Run forex analysis with natural language query."""
    # Default query
    query = "EUR/USD"

    # Check if query provided as command line argument
    if len(sys.argv) > 1:
        # Join all arguments to support multi-word queries
        query = " ".join(sys.argv[1:])

    try:
        # Initialize system
        print("🚀 Initializing Forex Agent System (v2 - Natural Language)...")
        system = ForexAgentSystem()

        # Run analysis with natural language
        result = system.analyze(query)

        # Print detailed results
        print("\n" + "=" * 60)
        print("📊 DETAILED RESULTS")
        print("=" * 60)

        # Query context
        query_ctx = result.get("query_context", {})
        if query_ctx:
            print(f"\n🔍 Query Understanding:")
            print(f"   Original: '{result['user_query']}'")
            print(f"   Parsed Pair: {query_ctx.get('pair', 'N/A')}")
            print(f"   Asset Type: {query_ctx.get('asset_type', 'N/A')}")
            print(f"   Timeframe: {query_ctx.get('timeframe', 'N/A')}")
            print(f"   Intent: {query_ctx.get('user_intent', 'N/A')}")

        # Agent summaries
        print("\n📰 News Agent:")
        news = result["agent_results"]["news"]
        if news and news.get("success"):
            print(f"   {news['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {news.get('error', 'Unknown error')}")

        print("\n📊 Technical Agent:")
        tech = result["agent_results"]["technical"]
        if tech and tech.get("success"):
            print(f"   {tech['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {tech.get('error', 'Unknown error')}")

        print("\n💰 Fundamental Agent:")
        fund = result["agent_results"]["fundamental"]
        if fund and fund.get("success"):
            print(f"   {fund['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {fund.get('error', 'Unknown error')}")

        print("\n⚖️  Risk Agent:")
        risk = result["agent_results"]["risk"]
        if risk and risk.get("success"):
            print(f"   {risk['data'].get('summary', 'N/A')}")
        else:
            print(f"   ❌ Error: {risk.get('error', 'Unknown error')}")

        print("\n" + "=" * 60)
        print("✅ Analysis complete!")
        print("\n💡 Try these queries:")
        print("   python main.py 'Analyze gold trading'")
        print("   python main.py 'Should I buy Bitcoin?'")
        print("   python main.py 'GBP/USD long term outlook'")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set GOOGLE_AI_API_KEY in .env file")
        print("Get your key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
