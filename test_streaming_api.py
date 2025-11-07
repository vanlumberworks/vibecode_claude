"""Test script for the streaming API."""

import sys
import json
import time
import requests
from sseclient import SSEClient  # pip install sseclient-py


def test_health_endpoint():
    """Test the health check endpoint."""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_info_endpoint():
    """Test the system info endpoint."""
    print("=" * 60)
    print("Testing Info Endpoint")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/info", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_non_streaming_analysis():
    """Test the non-streaming analysis endpoint."""
    print("=" * 60)
    print("Testing Non-Streaming Analysis Endpoint")
    print("=" * 60)

    query = "Analyze gold trading"
    print(f"Query: {query}\n")

    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json={"query": query},
            timeout=60
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\nDecision:")
            decision = result.get("decision", {})
            print(f"  Action: {decision.get('action', 'N/A')}")
            print(f"  Confidence: {decision.get('confidence', 0) * 100:.0f}%")

            if decision.get("reasoning", {}).get("summary"):
                print(f"\n  Summary: {decision['reasoning']['summary']}")

            print("\n✓ Non-streaming analysis completed successfully\n")
            return True
        else:
            print(f"Error: {response.text}\n")
            return False

    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_streaming_analysis(query="Analyze EUR/USD"):
    """Test the streaming analysis endpoint."""
    print("=" * 60)
    print("Testing Streaming Analysis Endpoint")
    print("=" * 60)

    print(f"Query: {query}\n")
    print("Streaming events:")
    print("-" * 60)

    try:
        # Create SSE client
        url = f"http://localhost:8000/analyze/stream?query={query}"
        messages = SSEClient(url)

        event_count = 0
        start_time = time.time()

        for msg in messages:
            if not msg.data:
                continue

            event_count += 1
            event_type = msg.event or "message"

            try:
                data = json.loads(msg.data)

                # Print event based on type
                if event_type == "start":
                    print(f"🚀 START: Analysis initiated")

                elif event_type == "query_parsed":
                    pair = data.get("pair", "Unknown")
                    print(f"🔍 QUERY PARSED: {pair}")

                elif event_type == "agent_update":
                    agent = data.get("agent", "unknown")
                    success = data.get("result", {}).get("success", False)
                    status = "✓" if success else "✗"
                    print(f"{status} AGENT: {agent.upper()} completed")

                elif event_type == "risk_update":
                    approved = data.get("trade_approved", False)
                    status = "APPROVED" if approved else "REJECTED"
                    print(f"⚖️  RISK: {status}")

                elif event_type == "decision":
                    decision = data.get("decision", {})
                    action = decision.get("action", "UNKNOWN")
                    confidence = decision.get("confidence", 0) * 100
                    print(f"📊 DECISION: {action} (Confidence: {confidence:.0f}%)")

                elif event_type == "complete":
                    elapsed = time.time() - start_time
                    print(f"✅ COMPLETE: Analysis finished in {elapsed:.2f}s")

                    result = data.get("result", {})
                    decision = result.get("decision", {})

                    print("\n" + "=" * 60)
                    print("Final Result:")
                    print("=" * 60)
                    print(f"Action: {decision.get('action', 'N/A')}")
                    print(f"Confidence: {decision.get('confidence', 0) * 100:.0f}%")

                    if decision.get("reasoning", {}).get("summary"):
                        print(f"\nSummary:\n{decision['reasoning']['summary']}")

                elif event_type == "error":
                    error = data.get("error", "Unknown error")
                    print(f"❌ ERROR: {error}")

            except json.JSONDecodeError:
                print(f"Warning: Could not parse event data: {msg.data}")

        print("\n" + "=" * 60)
        print(f"Streaming test completed: {event_count} events received")
        print("=" * 60 + "\n")

        return event_count > 0

    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Forex Agent System - Streaming API Tests")
    print("=" * 60 + "\n")

    # Check if server is running
    print("Checking if API server is running...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✓ API server is running\n")
    except Exception as e:
        print("✗ API server is not running!")
        print("\nPlease start the server first:")
        print("  python backend/server.py")
        print("\nOr:")
        print("  uvicorn backend.server:app --reload\n")
        sys.exit(1)

    # Run tests
    results = {
        "Health Check": test_health_endpoint(),
        "System Info": test_info_endpoint(),
        "Non-Streaming Analysis": test_non_streaming_analysis(),
        "Streaming Analysis": test_streaming_analysis(),
    }

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
