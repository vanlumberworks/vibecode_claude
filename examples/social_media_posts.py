"""
Example: Generating Social Media Posts from Trading Analysis

This demonstrates how to:
1. Run trading analysis
2. Format results for different social platforms
3. Handle both trading signals and informational posts
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from system import ForexAgentSystem
from utils.social_formatter import (
    format_for_twitter,
    format_for_telegram,
    format_for_facebook,
    format_all_platforms,
    is_trading_signal
)


def example_trading_signal():
    """Example: Generate posts for a trading signal."""
    print("=" * 80)
    print("Example 1: Trading Signal Posts")
    print("=" * 80)

    # Initialize system
    system = ForexAgentSystem()

    # Run analysis
    print("\n🔍 Analyzing EUR/USD...")
    result = system.analyze("Should I buy EUR/USD?")

    # Check if it's a trading signal
    if is_trading_signal(result):
        print("✅ Trading signal detected\n")
    else:
        print("ℹ️  Informational analysis (no clear signal)\n")

    # Generate posts for each platform
    print("-" * 80)
    print("TWITTER POST:")
    print("-" * 80)
    twitter_post = format_for_twitter(result, include_trade_params=True)
    print(twitter_post)
    print(f"\n📊 Character count: {len(twitter_post)}/280\n")

    print("-" * 80)
    print("TELEGRAM POST:")
    print("-" * 80)
    telegram_post = format_for_telegram(
        result,
        include_trade_params=True,
        channel_name="FX Signals Pro"
    )
    print(telegram_post)
    print()

    print("-" * 80)
    print("FACEBOOK POST:")
    print("-" * 80)
    facebook_post = format_for_facebook(
        result,
        include_trade_params=True,
        educational_context=True
    )
    print(facebook_post)
    print()


def example_informational_post():
    """Example: Generate posts for informational content (no trade params)."""
    print("\n" + "=" * 80)
    print("Example 2: Informational Post (No Trade Parameters)")
    print("=" * 80)

    # Initialize system
    system = ForexAgentSystem()

    # Run analysis
    print("\n🔍 Analyzing gold market...")
    result = system.analyze("What's happening with gold prices?")

    # Generate informational posts (no trade params)
    print("-" * 80)
    print("TWITTER POST (Informational):")
    print("-" * 80)
    twitter_post = format_for_twitter(
        result,
        include_trade_params=False,  # Don't show trade params
        custom_hashtags=["#Gold", "#XAU", "#CommodityTrading"]
    )
    print(twitter_post)
    print()

    print("-" * 80)
    print("TELEGRAM POST (Informational):")
    print("-" * 80)
    telegram_post = format_for_telegram(result, include_trade_params=False)
    print(telegram_post)
    print()


def example_all_platforms():
    """Example: Generate all posts at once."""
    print("\n" + "=" * 80)
    print("Example 3: Generate All Platforms at Once")
    print("=" * 80)

    # Initialize system
    system = ForexAgentSystem()

    # Run analysis
    print("\n🔍 Analyzing BTC/USD...")
    result = system.analyze("Bitcoin trading opportunity")

    # Generate all posts
    posts = format_all_platforms(
        result,
        include_trade_params=True,
        custom_options={
            'twitter_hashtags': ["#Bitcoin", "#BTC", "#Crypto"],
            'telegram_channel': "Crypto Trading Signals",
            'facebook_educational': True
        }
    )

    print("-" * 80)
    print("TWITTER:")
    print("-" * 80)
    print(posts['twitter'])
    print()

    print("-" * 80)
    print("TELEGRAM:")
    print("-" * 80)
    print(posts['telegram'])
    print()

    print("-" * 80)
    print("FACEBOOK:")
    print("-" * 80)
    print(posts['facebook'])
    print()


def example_frontend_integration():
    """
    Example: How a frontend would use this.

    Typical flow:
    1. User analyzes a pair via frontend
    2. Frontend stores the result
    3. User clicks "Share to Twitter" button
    4. Frontend calls format_for_twitter(result) and displays preview
    5. User confirms and posts
    """
    print("\n" + "=" * 80)
    print("Example 4: Frontend Integration Pattern")
    print("=" * 80)

    # Simulate backend API response
    analysis_result = {
        'pair': 'GBP/USD',
        'decision': 'SELL',
        'entry_price': 1.2650,
        'stop_loss': 1.2700,
        'target_price': 1.2550,
        'risk_reward_ratio': 2.0,
        'confidence': 'High',
        'reasoning': 'GBP weakening on BOE dovish stance. Technical resistance at 1.2700. Target support at 1.2550.',
        'citations': [
            {'title': 'BOE Rate Decision', 'url': 'https://example.com/boe'},
            {'title': 'GBP Technical Analysis', 'url': 'https://example.com/tech'}
        ]
    }

    print("\n📡 Frontend receives analysis result from backend...")
    print(f"✅ Pair: {analysis_result['pair']}")
    print(f"✅ Decision: {analysis_result['decision']}\n")

    # User clicks "Share to Twitter"
    print("👤 User clicks: 'Share to Twitter'")
    twitter_preview = format_for_twitter(analysis_result)
    print("\n📱 Preview shown to user:")
    print("-" * 40)
    print(twitter_preview)
    print("-" * 40)

    # User clicks "Share to Telegram"
    print("\n👤 User clicks: 'Share to Telegram'")
    telegram_preview = format_for_telegram(
        analysis_result,
        channel_name="My Trading Channel"
    )
    print("\n📱 Preview shown to user:")
    print("-" * 40)
    print(telegram_preview)
    print("-" * 40)

    print("\n✅ User can now copy or post directly via API\n")


def main():
    """Run all examples."""
    print("\n🎯 Social Media Post Formatter Examples\n")

    # Example 1: Trading signal
    example_trading_signal()

    # Example 2: Informational post
    example_informational_post()

    # Example 3: All platforms
    example_all_platforms()

    # Example 4: Frontend integration
    example_frontend_integration()

    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)
    print("\n💡 Integration Tips:")
    print("   1. Store analysis results in your database")
    print("   2. Let users preview posts before sharing")
    print("   3. Use include_trade_params=False for informational content")
    print("   4. Customize hashtags and channel names per user preferences")
    print("   5. Always include disclaimers (automatically added)")
    print()


if __name__ == "__main__":
    main()
