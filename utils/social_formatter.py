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
    decision = result.get('decision', 'WAIT')
    pair = result.get('pair', 'N/A')
    reasoning = result.get('reasoning', '')

    # Check if this is a trading signal
    is_signal = decision in ['BUY', 'SELL'] and include_trade_params

    if is_signal:
        entry = result.get('entry_price', 'N/A')
        stop_loss = result.get('stop_loss', 'N/A')
        target = result.get('target_price', 'N/A')

        # Ultra-concise format for signals
        emoji = "🟢" if decision == "BUY" else "🔴"
        post = (
            f"{emoji} {pair} {decision} @ {entry}\n"
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
    decision = result.get('decision', 'WAIT')
    pair = result.get('pair', 'N/A')
    reasoning = result.get('reasoning', '')
    confidence = result.get('confidence', 'Medium')

    # Header
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "WAIT": "⏸️"}
    emoji = emoji_map.get(decision, "📊")

    post = f"{emoji} **{pair} - {decision} Signal**\n\n"

    if channel_name:
        post = f"📡 **{channel_name}**\n\n" + post

    # Trading parameters
    is_signal = decision in ['BUY', 'SELL'] and include_trade_params

    if is_signal:
        entry = result.get('entry_price', 'N/A')
        stop_loss = result.get('stop_loss', 'N/A')
        target = result.get('target_price', 'N/A')
        risk_reward = result.get('risk_reward_ratio', 'N/A')

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
    if 'citations' in result and result['citations']:
        post += "**Sources:**\n"
        for i, citation in enumerate(result['citations'][:3], 1):  # Max 3 sources
            title = citation.get('title', 'Source')
            url = citation.get('url', '#')
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
    decision = result.get('decision', 'WAIT')
    pair = result.get('pair', 'N/A')
    reasoning = result.get('reasoning', '')

    # Friendly opening
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "WAIT": "⏸️"}
    emoji = emoji_map.get(decision, "📊")

    is_signal = decision in ['BUY', 'SELL'] and include_trade_params

    if is_signal:
        post = f"{emoji} **{pair} Trading Analysis - {decision} Setup**\n\n"
    else:
        post = f"{emoji} **{pair} Market Analysis**\n\n"

    # Main analysis
    post += f"{reasoning}\n\n"

    # Trade parameters in readable format
    if is_signal:
        entry = result.get('entry_price', 'N/A')
        stop_loss = result.get('stop_loss', 'N/A')
        target = result.get('target_price', 'N/A')
        risk_reward = result.get('risk_reward_ratio', 'N/A')

        post += "**📋 Trade Setup:**\n"
        post += f"Direction: {decision}\n"
        post += f"Entry Level: {entry}\n"
        post += f"Profit Target: {target}\n"
        post += f"Stop Loss: {stop_loss}\n"
        post += f"Risk/Reward Ratio: {risk_reward}\n\n"

    # Educational context for broader audience
    if educational_context:
        if decision == "BUY":
            post += "💡 **What does this mean?**\n"
            post += f"This analysis suggests {pair} may strengthen. "
            post += "Traders might consider long positions with proper risk management.\n\n"
        elif decision == "SELL":
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
    decision = result.get('decision', 'WAIT')
    has_params = all(key in result for key in ['entry_price', 'stop_loss', 'target_price'])
    return decision in ['BUY', 'SELL'] and has_params
