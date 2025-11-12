"""
Tests for Social Media Formatter (Updated for Nested Structure)

Validates formatting logic for Twitter, Telegram, and Facebook posts with correct result structure.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.social_formatter import (
    format_for_twitter,
    format_for_telegram,
    format_for_facebook,
    format_all_platforms,
    is_trading_signal,
    copy_to_clipboard
)


def create_buy_signal():
    """Create sample BUY signal with correct nested structure."""
    return {
        'pair': 'EUR/USD',
        'decision': {
            'action': 'BUY',
            'confidence': 0.85,
            'reasoning': {
                'summary': 'Strong bullish momentum with ECB rate hike expectations. Technical breakout confirmed.'
            },
            'trade_parameters': {
                'entry_price': 1.0850,
                'stop_loss': 1.0800,
                'take_profit': 1.0950
            },
            'grounding_metadata': {
                'sources': [
                    {'title': 'ECB Policy Update', 'url': 'https://example.com/ecb'},
                    {'title': 'EUR Technical Analysis', 'url': 'https://example.com/tech'}
                ]
            }
        }
    }


def create_sell_signal():
    """Create sample SELL signal."""
    return {
        'pair': 'GBP/USD',
        'decision': {
            'action': 'SELL',
            'confidence': 0.78,
            'reasoning': {
                'summary': 'GBP weakening on BOE dovish stance.'
            },
            'trade_parameters': {
                'entry_price': 1.2650,
                'stop_loss': 1.2700,
                'take_profit': 1.2550
            }
        }
    }


def create_wait_signal():
    """Create sample WAIT signal (informational)."""
    return {
        'pair': 'XAU/USD',
        'decision': {
            'action': 'WAIT',
            'confidence': 0.5,
            'reasoning': {
                'summary': 'Gold consolidating near key support. Awaiting Fed decision before taking position.'
            }
        }
    }


def test_twitter_buy_signal():
    """Test Twitter formatting for BUY signals."""
    print("\n" + "=" * 80)
    print("TEST 1: Twitter - BUY Signal (Nested Structure)")
    print("=" * 80)

    result = create_buy_signal()
    post = format_for_twitter(result, include_trade_params=True)

    print(post)
    print(f"\n✅ Length: {len(post)} chars")

    # Assertions
    assert len(post) <= 280, f"❌ Post exceeds 280 chars: {len(post)}"
    assert '🟢' in post, "❌ Missing BUY emoji"
    assert 'EUR/USD' in post, "❌ Missing pair"
    assert 'BUY' in post, "❌ Missing BUY action"
    assert 'NFA' in post or 'DYOR' in post, "❌ Missing disclaimer"
    assert '#' in post, "❌ Missing hashtags"

    print("✅ All assertions passed!\n")


def test_twitter_sell_signal():
    """Test Twitter formatting for SELL signals."""
    print("=" * 80)
    print("TEST 2: Twitter - SELL Signal")
    print("=" * 80)

    result = create_sell_signal()
    post = format_for_twitter(result)

    print(post)
    print(f"\n✅ Length: {len(post)} chars")

    assert len(post) <= 280, f"❌ Post exceeds 280 chars"
    assert '🔴' in post, "❌ Missing SELL emoji"
    assert 'SELL' in post, "❌ Missing SELL keyword"

    print("✅ All assertions passed!\n")


def test_telegram_with_sources():
    """Test Telegram formatting with citations."""
    print("=" * 80)
    print("TEST 3: Telegram - With Sources")
    print("=" * 80)

    result = create_buy_signal()
    post = format_for_telegram(result, channel_name="FX Signals Pro")

    print(post)

    # Assertions
    assert '**' in post, "❌ Missing markdown bold"
    assert 'Entry:' in post, "❌ Missing entry price"
    assert 'Target:' in post, "❌ Missing target"
    assert 'Stop Loss:' in post, "❌ Missing stop loss"
    assert 'Disclaimer' in post, "❌ Missing disclaimer"
    assert 'FX Signals Pro' in post, "❌ Missing channel name"
    assert 'ECB Policy Update' in post, "❌ Missing citations"

    print("✅ All assertions passed!\n")


def test_facebook_trading_signal():
    """Test Facebook formatting with educational context."""
    print("=" * 80)
    print("TEST 4: Facebook - Trading Signal")
    print("=" * 80)

    result = create_buy_signal()
    post = format_for_facebook(result, educational_context=True)

    print(post)

    # Assertions
    assert 'Trade Setup:' in post, "❌ Missing trade setup"
    assert 'Entry Level:' in post, "❌ Missing entry"
    assert 'What does this mean?' in post, "❌ Missing educational context"
    assert 'DISCLAIMER' in post.upper(), "❌ Missing disclaimer"
    assert '#' in post, "❌ Missing hashtags"

    print("✅ All assertions passed!\n")


def test_format_all_platforms():
    """Test generating all platforms at once."""
    print("=" * 80)
    print("TEST 5: Format All Platforms")
    print("=" * 80)

    result = create_sell_signal()
    posts = format_all_platforms(result)

    print("Twitter:")
    print("-" * 40)
    print(posts['twitter'])
    print()

    print("Telegram (first 200 chars):")
    print("-" * 40)
    print(posts['telegram'][:200] + "...")
    print()

    print("Facebook (first 200 chars):")
    print("-" * 40)
    print(posts['facebook'][:200] + "...")
    print()

    # Assertions
    assert 'twitter' in posts, "❌ Missing Twitter post"
    assert 'telegram' in posts, "❌ Missing Telegram post"
    assert 'facebook' in posts, "❌ Missing Facebook post"
    assert len(posts['twitter']) <= 280, "❌ Twitter post too long"

    print("✅ All assertions passed!\n")


def test_is_trading_signal_detection():
    """Test trading signal detection."""
    print("=" * 80)
    print("TEST 6: Trading Signal Detection")
    print("=" * 80)

    # Valid BUY signal
    buy_signal = create_buy_signal()
    assert is_trading_signal(buy_signal) == True, "❌ Should be trading signal"
    print("✅ BUY signal detected correctly")

    # WAIT signal (not a trading signal)
    wait_signal = create_wait_signal()
    assert is_trading_signal(wait_signal) == False, "❌ WAIT should not be a signal"
    print("✅ WAIT correctly identified as not a signal")

    # Incomplete signal (missing parameters)
    incomplete = {
        'pair': 'EUR/USD',
        'decision': {
            'action': 'BUY',
            'reasoning': {'summary': 'Test'}
        }
    }
    assert is_trading_signal(incomplete) == False, "❌ Incomplete should not be signal"
    print("✅ Incomplete data correctly rejected")

    print("\n✅ All signal detection tests passed!\n")


def test_copy_to_clipboard():
    """Test copy to clipboard function."""
    print("=" * 80)
    print("TEST 7: Copy to Clipboard")
    print("=" * 80)

    test_text = "Test social media post"
    result = copy_to_clipboard(test_text)

    if result:
        print("✅ Text copied to clipboard successfully")
        print(f"   Content: \"{test_text}\"")
    else:
        print("⚠️  Clipboard copy not available (pyperclip not installed)")
        print("   This is expected if pyperclip is not installed")

    print()


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 SOCIAL FORMATTER TEST SUITE (Updated for Nested Structure)")
    print("=" * 80)

    try:
        test_twitter_buy_signal()
        test_twitter_sell_signal()
        test_telegram_with_sources()
        test_facebook_trading_signal()
        test_format_all_platforms()
        test_is_trading_signal_detection()
        test_copy_to_clipboard()

        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📊 Summary:")
        print("   • Twitter formatting: ✅")
        print("   • Telegram formatting: ✅")
        print("   • Facebook formatting: ✅")
        print("   • Signal detection: ✅")
        print("   • Copy to clipboard: ✅")
        print("   • Nested structure handling: ✅")
        print()

    except AssertionError as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED!")
        print("=" * 80)
        print(f"Error: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()
