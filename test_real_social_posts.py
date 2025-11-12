"""
Test social formatters with REAL analysis from ForexAgentSystem
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from system import ForexAgentSystem
from utils.social_formatter import (
    format_for_twitter,
    format_for_telegram,
    format_for_facebook,
    format_all_platforms,
    is_trading_signal,
    copy_to_clipboard
)


def test_with_real_analysis():
    """Test formatters with real analysis result."""
    print("\n" + "=" * 80)
    print("🧪 TESTING WITH REAL FOREX AGENT SYSTEM ANALYSIS")
    print("=" * 80)

    # Initialize system
    print("\n📊 Initializing Forex Agent System...")
    system = ForexAgentSystem()

    # Run analysis
    print("\n🔍 Running analysis on EUR/USD...\n")
    result = system.analyze("EUR/USD", verbose=True)

    print("\n" + "=" * 80)
    print("📋 RESULT STRUCTURE:")
    print("=" * 80)
    print(f"Pair: {result.get('pair')}")
    print(f"Decision Action: {result.get('decision', {}).get('action')}")
    print(f"Confidence: {result.get('decision', {}).get('confidence')}")
    print(f"Has Trade Params: {result.get('decision', {}).get('trade_parameters') is not None}")

    # Check if it's a trading signal
    is_signal = is_trading_signal(result)
    print(f"\nIs Trading Signal: {is_signal}")

    # Generate social media posts
    print("\n" + "=" * 80)
    print("📱 GENERATING SOCIAL MEDIA POSTS")
    print("=" * 80)

    # Twitter
    print("\n" + "-" * 80)
    print("TWITTER POST:")
    print("-" * 80)
    twitter_post = format_for_twitter(result)
    print(twitter_post)
    print(f"\nLength: {len(twitter_post)}/280 chars")

    # Telegram
    print("\n" + "-" * 80)
    print("TELEGRAM POST:")
    print("-" * 80)
    telegram_post = format_for_telegram(result, channel_name="FX Pro Signals")
    print(telegram_post)

    # Facebook
    print("\n" + "-" * 80)
    print("FACEBOOK POST:")
    print("-" * 80)
    facebook_post = format_for_facebook(result)
    print(facebook_post)

    # Test copy to clipboard
    print("\n" + "-" * 80)
    print("COPY TO CLIPBOARD TEST:")
    print("-" * 80)
    if copy_to_clipboard(twitter_post):
        print("✅ Twitter post copied to clipboard!")
        print("   You can now paste it anywhere (Ctrl+V / Cmd+V)")
    else:
        print("⚠️  Clipboard not available (install pyperclip)")

    print("\n" + "=" * 80)
    print("✅ REAL ANALYSIS TEST COMPLETE!")
    print("=" * 80)
    print("\n💡 Next Steps:")
    print("   1. Review the generated posts above")
    print("   2. Verify formatting looks correct")
    print("   3. Test copy-paste into actual social platforms")
    print("   4. Integrate into your frontend/backend")
    print()


if __name__ == "__main__":
    test_with_real_analysis()
