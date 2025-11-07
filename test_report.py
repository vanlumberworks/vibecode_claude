"""Test script to verify report generation works."""

import os
from dotenv import load_dotenv
load_dotenv()

# Check if API key exists
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key:
    print("❌ GOOGLE_AI_API_KEY not found in environment")
    print("Please set it in .env file")
    exit(1)

print("Testing report generation node...")
print("=" * 60)

from system import ForexAgentSystem

try:
    # Initialize system
    print("\n1. Initializing system...")
    system = ForexAgentSystem()

    # Run analysis
    print("\n2. Running analysis for EUR/USD...")
    result = system.analyze("EUR/USD", verbose=True)

    # Check report
    print("\n3. Checking report generation...")
    if "report" in result:
        report = result["report"]
        if report:
            success = report.get("success", False)
            if success:
                html = report.get("html", "")
                metadata = report.get("metadata", {})
                word_count = metadata.get("word_count", 0)
                print(f"   ✅ Report generated successfully!")
                print(f"   📄 Word count: {word_count}")
                print(f"   📊 Sections: {metadata.get('sections', [])}")
                print(f"\n   First 500 characters of HTML:")
                print(f"   {html[:500]}...")
            else:
                print(f"   ❌ Report generation failed: {report.get('error', 'Unknown error')}")
        else:
            print("   ⚠️  Report is None (workflow may have ended early)")
    else:
        print("   ❌ 'report' key not found in result")

    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")

except Exception as e:
    print(f"\n❌ Test failed with error: {str(e)}")
    import traceback
    traceback.print_exc()
