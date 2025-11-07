"""Example client for consuming the streaming API.

This example demonstrates how to use the Forex Agent System streaming API
to get real-time updates as the analysis progresses.

Requirements:
    pip install sseclient-py requests

Usage:
    python examples/streaming_client.py "Analyze gold trading"
    python examples/streaming_client.py "EUR/USD"
    python examples/streaming_client.py "Should I buy Bitcoin?"
"""

import sys
import json
import time
from sseclient import SSEClient


def analyze_with_streaming(query: str, api_url: str = "http://localhost:8000"):
    """
    Analyze a trading query with streaming updates.

    Args:
        query: Natural language query or currency pair
        api_url: Base URL of the API server

    Returns:
        Final analysis result
    """
    print(f"\n{'=' * 60}")
    print(f"🔍 Query: {query}")
    print(f"{'=' * 60}\n")

    # Create streaming URL
    stream_url = f"{api_url}/analyze/stream?query={query}"

    # Track state
    start_time = time.time()
    final_result = None

    try:
        # Connect to SSE stream
        messages = SSEClient(stream_url)

        for msg in messages:
            if not msg.data:
                continue

            event_type = msg.event or "message"
            data = json.loads(msg.data)

            # Handle different event types
            if event_type == "start":
                print("🚀 Analysis started...")

            elif event_type == "query_parsed":
                query_context = data.get("query_context", {})
                pair = data.get("pair", "Unknown")
                asset_type = query_context.get("asset_type", "unknown")
                print(f"📋 Parsed Query:")
                print(f"   Pair: {pair}")
                print(f"   Asset Type: {asset_type}")
                print(f"   Timeframe: {query_context.get('timeframe', 'N/A')}")
                print("\n⏳ Running analysis agents...")

            elif event_type == "agent_update":
                agent = data.get("agent", "unknown")
                result = data.get("result", {})
                success = result.get("success", False)

                agent_emoji = {
                    "news": "📰",
                    "technical": "📊",
                    "fundamental": "💼"
                }
                emoji = agent_emoji.get(agent, "🤖")

                if success:
                    print(f"   {emoji} {agent.title()} Agent: ✓ Complete")
                else:
                    print(f"   {emoji} {agent.title()} Agent: ✗ Failed")

            elif event_type == "risk_update":
                risk_result = data.get("risk_result", {})
                approved = data.get("trade_approved", False)

                print(f"\n⚖️  Risk Assessment: {'APPROVED' if approved else 'REJECTED'}")

                if not approved and risk_result.get("data", {}).get("rejection_reason"):
                    print(f"   Reason: {risk_result['data']['rejection_reason']}")

                if approved:
                    print("\n💭 Synthesizing final decision...")

            elif event_type == "decision":
                decision = data.get("decision", {})
                action = decision.get("action", "UNKNOWN")
                confidence = decision.get("confidence", 0)

                action_emoji = {
                    "BUY": "🟢",
                    "SELL": "🔴",
                    "WAIT": "🟡"
                }
                emoji = action_emoji.get(action, "❓")

                print(f"\n{emoji} Decision: {action}")
                print(f"   Confidence: {confidence * 100:.0f}%")

            elif event_type == "complete":
                elapsed = time.time() - start_time
                final_result = data.get("result", {})

                print(f"\n{'=' * 60}")
                print(f"✅ Analysis Complete ({elapsed:.2f}s)")
                print(f"{'=' * 60}")

                # Print detailed result
                print_result(final_result)

            elif event_type == "error":
                error = data.get("error", "Unknown error")
                error_type = data.get("error_type", "Error")
                print(f"\n❌ {error_type}: {error}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        return None

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

    return final_result


def print_result(result: dict):
    """Print the final analysis result in a readable format."""
    decision = result.get("decision", {})

    if not decision:
        print("\n⚠️  No decision made")
        return

    action = decision.get("action", "UNKNOWN")
    confidence = decision.get("confidence", 0)

    print(f"\nFinal Decision: {action}")
    print(f"Confidence: {confidence * 100:.0f}%")

    # Print reasoning
    reasoning = decision.get("reasoning", {})
    if reasoning.get("summary"):
        print(f"\nSummary:")
        print(f"  {reasoning['summary']}")

    # Print key factors
    if reasoning.get("key_factors"):
        print(f"\nKey Factors:")
        for factor in reasoning["key_factors"]:
            print(f"  • {factor}")

    # Print trade parameters
    if action in ["BUY", "SELL"]:
        params = decision.get("trade_parameters", {})
        if params:
            print(f"\nTrade Parameters:")
            print(f"  Entry Price: {params.get('entry_price', 'N/A')}")
            print(f"  Stop Loss: {params.get('stop_loss', 'N/A')}")
            print(f"  Take Profit: {params.get('take_profit', 'N/A')}")
            print(f"  Position Size: {params.get('position_size', 'N/A')} lots")

    # Print sources
    grounding = decision.get("grounding_metadata", {})
    sources = grounding.get("sources", [])
    if sources:
        print(f"\n🌐 Sources ({len(sources)}):")
        for i, source in enumerate(sources[:5], 1):
            print(f"  {i}. {source.get('title', 'Unknown')}")
            print(f"     {source.get('url', 'No URL')}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python examples/streaming_client.py <query>")
        print("\nExamples:")
        print('  python examples/streaming_client.py "Analyze gold trading"')
        print('  python examples/streaming_client.py "EUR/USD"')
        print('  python examples/streaming_client.py "Should I buy Bitcoin?"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Check if API server is running
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  API server is not healthy")
            sys.exit(1)
    except Exception:
        print("❌ Could not connect to API server at http://localhost:8000")
        print("\nPlease start the server first:")
        print("  python backend/server.py")
        print("\nOr:")
        print("  uvicorn backend.server:app --reload")
        sys.exit(1)

    # Run streaming analysis
    result = analyze_with_streaming(query)

    if result:
        print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    main()
