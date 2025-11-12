"""
Social Media Post Formatter for FX Trading Analysis

Converts trading analysis results into platform-specific social media posts.
Supports Twitter, Telegram, and Facebook with professional FX trader voice.
"""

from typing import Dict, Any, Optional


def format_for_twitter(
    result: Dict[str, Any],
    include_trade_params: bool = True,
    custom_hashtags: Optional[list] = None
) -> str:
    """
    Format analysis result for Twitter (280 character limit).

    Args:
        result: Analysis result from ForexAgentSystem.analyze()
        include_trade_params: Include entry/stop/target if available
        custom_hashtags: List of custom hashtags (defaults to #Forex #Trading)

    Returns:
        Formatted tweet string (max 280 chars)
    """
    decision_data = result.get('decision', {})
    action = decision_data.get('action', 'WAIT') if isinstance(decision_data, dict) else decision_data
    pair = result.get('pair', 'N/A')

    # Get reasoning - handle both nested and flat structures
    reasoning_data = decision_data.get('reasoning', {}) if isinstance(decision_data, dict) else {}
    reasoning = reasoning_data.get('summary', '') if isinstance(reasoning_data, dict) else str(reasoning_data)

    # Check if this is a trading signal
    is_signal = action in ['BUY', 'SELL'] and include_trade_params

    if is_signal:
        # Get trade parameters from nested structure
        trade_params = decision_data.get('trade_parameters', {}) if isinstance(decision_data, dict) else {}
        entry = trade_params.get('entry_price', 'N/A')
        stop_loss = trade_params.get('stop_loss', 'N/A')
        target = trade_params.get('take_profit', trade_params.get('target_price', 'N/A'))  # Handle both names

        # Ultra-concise format for signals
        emoji = "🟢" if action == "BUY" else "🔴"
        post = (
            f"{emoji} {pair} {action} @ {entry}\n"
            f"🎯 Target: {target} | 🛡️ Stop: {stop_loss}\n"
        )

        # Add brief reasoning if space allows
        if len(post) < 200:
            reason_snippet = reasoning[:70] + "..." if len(reasoning) > 70 else reasoning
            post += f"{reason_snippet}\n"
    else:
        # Informational post
        emoji = "📊"
        # Extract key insight from reasoning
        insight = reasoning[:150] + "..." if len(reasoning) > 150 else reasoning
        post = f"{emoji} {pair} Market Analysis\n\n{insight}\n"

    # Add hashtags
    hashtags = custom_hashtags or ["#Forex", "#Trading", f"#{pair.replace('/', '')}"]
    hashtag_str = " ".join(hashtags)

    # Add disclaimer + hashtags (ensure total under 280)
    disclaimer = "\n⚠️ NFA | DYOR"

    max_length = 280 - len(disclaimer) - len(hashtag_str) - 2  # 2 for spacing
    if len(post) > max_length:
        post = post[:max_length-3] + "..."

    return post + disclaimer + "\n" + hashtag_str


def format_for_telegram(
    result: Dict[str, Any],
    include_trade_params: bool = True,
    channel_name: Optional[str] = None
) -> str:
    """
    Format analysis result for Telegram (supports markdown).

    Args:
        result: Analysis result from ForexAgentSystem.analyze()
        include_trade_params: Include detailed trade parameters
        channel_name: Optional channel name for branding

    Returns:
        Formatted message with markdown
    """
    decision_data = result.get('decision', {})
    action = decision_data.get('action', 'WAIT') if isinstance(decision_data, dict) else decision_data
    pair = result.get('pair', 'N/A')

    # Get reasoning and confidence from nested structure
    reasoning_data = decision_data.get('reasoning', {}) if isinstance(decision_data, dict) else {}
    reasoning = reasoning_data.get('summary', '') if isinstance(reasoning_data, dict) else str(reasoning_data)
    confidence_pct = decision_data.get('confidence', 0.5) if isinstance(decision_data, dict) else 0.5
    confidence = f"{confidence_pct:.0%}" if isinstance(confidence_pct, (int, float)) else str(confidence_pct)

    # Header
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "WAIT": "⏸️"}
    emoji = emoji_map.get(action, "📊")

    post = f"{emoji} **{pair} - {action} Signal**\n\n"

    if channel_name:
        post = f"📡 **{channel_name}**\n\n" + post

    # Trading parameters
    is_signal = action in ['BUY', 'SELL'] and include_trade_params

    if is_signal:
        trade_params = decision_data.get('trade_parameters', {}) if isinstance(decision_data, dict) else {}
        entry = trade_params.get('entry_price', 'N/A')
        stop_loss = trade_params.get('stop_loss', 'N/A')
        target = trade_params.get('take_profit', trade_params.get('target_price', 'N/A'))

        # Calculate risk/reward if we have the data
        risk_reward = 'N/A'
        if isinstance(entry, (int, float)) and isinstance(stop_loss, (int, float)) and isinstance(target, (int, float)):
            risk = abs(entry - stop_loss)
            reward = abs(target - entry)
            if risk > 0:
                risk_reward = f"{reward/risk:.1f}"

        post += "**Trade Parameters:**\n"
        post += f"• Entry: `{entry}`\n"
        post += f"• Target: `{target}`\n"
        post += f"• Stop Loss: `{stop_loss}`\n"
        post += f"• Risk/Reward: `{risk_reward}`\n"
        post += f"• Confidence: `{confidence}`\n\n"

    # Analysis reasoning
    post += "**Analysis:**\n"
    post += f"{reasoning}\n\n"

    # Citations if available
    grounding = decision_data.get('grounding_metadata', {}) if isinstance(decision_data, dict) else {}
    sources = grounding.get('sources', [])
    if sources:
        post += "**Sources:**\n"
        for i, source in enumerate(sources[:3], 1):  # Max 3 sources
            title = source.get('title', 'Source')
            url = source.get('url', '#')
            post += f"{i}. [{title}]({url})\n"
        post += "\n"

    # Disclaimer
    post += "---\n"
    post += "⚠️ **Disclaimer:** This is not financial advice. "
    post += "Trading forex involves significant risk. Always do your own research "
    post += "and consult with a qualified financial advisor before making trading decisions.\n"

    return post


def format_for_facebook(
    result: Dict[str, Any],
    include_trade_params: bool = True,
    educational_context: bool = True
) -> str:
    """
    Format analysis result for Facebook (more casual-professional tone).

    Args:
        result: Analysis result from ForexAgentSystem.analyze()
        include_trade_params: Include trade parameters
        educational_context: Add educational context for broader audience

    Returns:
        Formatted Facebook post
    """
    decision_data = result.get('decision', {})
    action = decision_data.get('action', 'WAIT') if isinstance(decision_data, dict) else decision_data
    pair = result.get('pair', 'N/A')

    # Get reasoning from nested structure
    reasoning_data = decision_data.get('reasoning', {}) if isinstance(decision_data, dict) else {}
    reasoning = reasoning_data.get('summary', '') if isinstance(reasoning_data, dict) else str(reasoning_data)

    # Friendly opening
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "WAIT": "⏸️"}
    emoji = emoji_map.get(action, "📊")

    is_signal = action in ['BUY', 'SELL'] and include_trade_params

    if is_signal:
        post = f"{emoji} **{pair} Trading Analysis - {action} Setup**\n\n"
    else:
        post = f"{emoji} **{pair} Market Analysis**\n\n"

    # Main analysis
    post += f"{reasoning}\n\n"

    # Trade parameters in readable format
    if is_signal:
        trade_params = decision_data.get('trade_parameters', {}) if isinstance(decision_data, dict) else {}
        entry = trade_params.get('entry_price', 'N/A')
        stop_loss = trade_params.get('stop_loss', 'N/A')
        target = trade_params.get('take_profit', trade_params.get('target_price', 'N/A'))

        # Calculate risk/reward
        risk_reward = 'N/A'
        if isinstance(entry, (int, float)) and isinstance(stop_loss, (int, float)) and isinstance(target, (int, float)):
            risk = abs(entry - stop_loss)
            reward = abs(target - entry)
            if risk > 0:
                risk_reward = f"{reward/risk:.1f}"

        post += "**📋 Trade Setup:**\n"
        post += f"Direction: {action}\n"
        post += f"Entry Level: {entry}\n"
        post += f"Profit Target: {target}\n"
        post += f"Stop Loss: {stop_loss}\n"
        post += f"Risk/Reward Ratio: {risk_reward}\n\n"

    # Educational context for broader audience
    if educational_context:
        if action == "BUY":
            post += "💡 **What does this mean?**\n"
            post += f"This analysis suggests {pair} may strengthen. "
            post += "Traders might consider long positions with proper risk management.\n\n"
        elif action == "SELL":
            post += "💡 **What does this mean?**\n"
            post += f"This analysis suggests {pair} may weaken. "
            post += "Traders might consider short positions with proper risk management.\n\n"
        else:
            post += "💡 **What does this mean?**\n"
            post += "Current conditions suggest waiting for clearer signals before entering positions.\n\n"

    # Comprehensive disclaimer
    post += "---\n\n"
    post += "⚠️ **IMPORTANT DISCLAIMER:**\n"
    post += "This post is for educational and informational purposes only and does NOT constitute financial advice. "
    post += "Trading foreign exchange (forex) carries a high level of risk and may not be suitable for all investors. "
    post += "Past performance is not indicative of future results. Always conduct your own research, "
    post += "understand the risks involved, and consult with a licensed financial advisor before making any trading decisions. "
    post += "Never trade with money you cannot afford to lose.\n\n"
    post += "#ForexTrading #MarketAnalysis #TradingEducation"

    return post


def format_all_platforms(
    result: Dict[str, Any],
    include_trade_params: bool = True,
    custom_options: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Generate posts for all platforms at once.

    Args:
        result: Analysis result from ForexAgentSystem.analyze()
        include_trade_params: Include trade parameters
        custom_options: Platform-specific options

    Returns:
        Dictionary with keys: 'twitter', 'telegram', 'facebook'
    """
    options = custom_options or {}

    return {
        'twitter': format_for_twitter(
            result,
            include_trade_params=include_trade_params,
            custom_hashtags=options.get('twitter_hashtags')
        ),
        'telegram': format_for_telegram(
            result,
            include_trade_params=include_trade_params,
            channel_name=options.get('telegram_channel')
        ),
        'facebook': format_for_facebook(
            result,
            include_trade_params=include_trade_params,
            educational_context=options.get('facebook_educational', True)
        )
    }


# Helper function to detect if result contains a trading signal
def is_trading_signal(result: Dict[str, Any]) -> bool:
    """Check if analysis result contains an actionable trading signal."""
    decision_data = result.get('decision', {})
    action = decision_data.get('action', 'WAIT') if isinstance(decision_data, dict) else decision_data

    # Check for trade parameters in nested structure
    trade_params = decision_data.get('trade_parameters', {}) if isinstance(decision_data, dict) else {}
    has_params = all(
        trade_params.get(key) is not None
        for key in ['entry_price', 'stop_loss']
    ) and (trade_params.get('take_profit') is not None or trade_params.get('target_price') is not None)

    return action in ['BUY', 'SELL'] and has_params


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard (for UX convenience).

    Args:
        text: Text to copy to clipboard

    Returns:
        True if successful, False otherwise

    Note:
        This uses pyperclip which needs to be installed: pip install pyperclip
        On Linux, may require xclip or xsel to be installed.
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        print("⚠️  pyperclip not installed. Run: pip install pyperclip")
        return False
    except Exception as e:
        print(f"⚠️  Could not copy to clipboard: {e}")
        return False
