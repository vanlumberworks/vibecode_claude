"""Query Parser Node - Transforms natural language to structured context."""

import json
import os
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from graph.state import ForexAgentState


def query_parser_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Parse natural language query into structured context using Gemini.

    This node enriches the user's input with:
    - Normalized currency pair (e.g., "gold" → "XAU/USD")
    - Asset type classification
    - Inferred timeframe
    - User intent
    - Risk preferences
    - Additional context

    Examples:
        "Analyze gold trading" → {"pair": "XAU/USD", "asset_type": "commodity", ...}
        "EUR/USD short term" → {"pair": "EUR/USD", "timeframe": "short_term", ...}
        "Should I buy Bitcoin?" → {"pair": "BTC/USD", "user_intent": "buy_signal", ...}

    Args:
        state: Current graph state with user_query
        config: Runtime configuration

    Returns:
        State updates with query_context
    """
    user_query = state.get("user_query", "")
    print(f"🔍 Query Parser analyzing: '{user_query}'")

    try:
        from google import genai
        from google.genai import types

        # Initialize Gemini client
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found in environment")

        client = genai.Client(api_key=api_key)

        # Build parser prompt
        prompt = _build_parser_prompt(user_query)

        # Configure Gemini for structured output
        config_gemini = types.GenerateContentConfig(
            temperature=0.1,  # Low temperature for consistent parsing
            response_mime_type="application/json",
        )

        # Parse query
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=config_gemini,
        )

        # Parse response
        query_context = json.loads(response.text)

        # Set backwards-compatible pair field
        pair = query_context.get("pair", "EUR/USD")

        print(f"  ✅ Parsed as: {pair} ({query_context.get('asset_type', 'unknown')})")
        print(f"     Timeframe: {query_context.get('timeframe', 'unknown')}")
        print(f"     Intent: {query_context.get('user_intent', 'unknown')}")

        return {
            "query_context": query_context,
            "pair": pair,  # For backwards compatibility
            "step_count": state.get("step_count", 0) + 1,
        }

    except Exception as e:
        print(f"  ❌ Query parsing failed: {str(e)}")

        # Fallback: try to extract pair from query
        fallback_pair = _fallback_parse(user_query)

        return {
            "query_context": {
                "pair": fallback_pair,
                "asset_type": "unknown",
                "parse_error": str(e),
            },
            "pair": fallback_pair,
            "step_count": state.get("step_count", 0) + 1,
            "errors": {**state.get("errors", {}), "query_parser": str(e)},
        }


def _build_parser_prompt(user_query: str) -> str:
    """Build the parsing prompt for Gemini."""
    return f"""You are a forex/crypto/commodity trading query parser. Your job is to transform natural language queries into structured JSON context.

USER QUERY: "{user_query}"

TASK:
Parse the user's query and extract the following information:

1. **Currency/Asset Pair**: Normalize to standard format (e.g., EUR/USD, XAU/USD, BTC/USD)
   - "gold" → "XAU/USD"
   - "bitcoin" → "BTC/USD"
   - "euro dollar" → "EUR/USD"
   - "EURUSD" → "EUR/USD"
   - If unclear, default to "EUR/USD"

2. **Asset Type**: Classify the asset
   - "forex" (currency pairs like EUR/USD)
   - "commodity" (gold, silver, oil, etc.)
   - "crypto" (bitcoin, ethereum, etc.)
   - "index" (stock indices)

3. **Base/Quote Currency**: Split the pair
   - EUR/USD → base: "EUR", quote: "USD"
   - XAU/USD → base: "XAU", quote: "USD"

4. **Timeframe**: Infer from context
   - "short_term" (scalping, day trading)
   - "medium_term" (swing trading, weekly)
   - "long_term" (position trading, monthly+)
   - Default: "short_term"

5. **User Intent**: What does the user want?
   - "trading_signal" (general analysis)
   - "buy_signal" (looking to buy)
   - "sell_signal" (looking to sell)
   - "market_overview" (just information)
   - "risk_assessment" (evaluate risk)

6. **Risk Tolerance**: Infer if mentioned
   - "conservative", "moderate", "aggressive"
   - Default: "moderate"

7. **Additional Context**: Any other relevant info
   - Specific indicators mentioned?
   - News events mentioned?
   - Price levels mentioned?

OUTPUT FORMAT (JSON):
{{
  "pair": "XAU/USD",
  "asset_type": "commodity",
  "base_currency": "XAU",
  "quote_currency": "USD",
  "timeframe": "short_term",
  "user_intent": "trading_signal",
  "risk_tolerance": "moderate",
  "additional_context": {{
    "keywords": ["gold", "trading"],
    "mentioned_indicators": [],
    "mentioned_events": [],
    "price_levels": []
  }},
  "confidence": 0.95
}}

EXAMPLES:

Input: "Analyze gold trading"
Output:
{{
  "pair": "XAU/USD",
  "asset_type": "commodity",
  "base_currency": "XAU",
  "quote_currency": "USD",
  "timeframe": "short_term",
  "user_intent": "trading_signal",
  "risk_tolerance": "moderate",
  "additional_context": {{"keywords": ["gold", "trading"]}},
  "confidence": 0.95
}}

Input: "Should I buy EUR/USD for long term?"
Output:
{{
  "pair": "EUR/USD",
  "asset_type": "forex",
  "base_currency": "EUR",
  "quote_currency": "USD",
  "timeframe": "long_term",
  "user_intent": "buy_signal",
  "risk_tolerance": "moderate",
  "additional_context": {{"keywords": ["long term", "buy"]}},
  "confidence": 1.0
}}

Input: "What's happening with Bitcoin?"
Output:
{{
  "pair": "BTC/USD",
  "asset_type": "crypto",
  "base_currency": "BTC",
  "quote_currency": "USD",
  "timeframe": "short_term",
  "user_intent": "market_overview",
  "risk_tolerance": "moderate",
  "additional_context": {{"keywords": ["bitcoin", "market"]}},
  "confidence": 0.9
}}

Now parse: "{user_query}"

Remember: Always output valid JSON. Be intelligent about synonyms and abbreviations.
"""


def _fallback_parse(user_query: str) -> str:
    """
    Fallback parser using simple keyword matching.
    Used when Gemini API fails.
    """
    query_lower = user_query.lower()

    # Common asset mappings
    mappings = {
        "gold": "XAU/USD",
        "silver": "XAG/USD",
        "oil": "CL/USD",
        "bitcoin": "BTC/USD",
        "btc": "BTC/USD",
        "ethereum": "ETH/USD",
        "eth": "ETH/USD",
        "euro": "EUR/USD",
        "pound": "GBP/USD",
        "yen": "USD/JPY",
    }

    # Check for direct matches
    for keyword, pair in mappings.items():
        if keyword in query_lower:
            return pair

    # Try to extract pair format (e.g., "EURUSD" or "EUR/USD")
    import re

    # Match patterns like EUR/USD or EURUSD
    pair_pattern = r"([A-Z]{3})[/\s]?([A-Z]{3})"
    match = re.search(pair_pattern, user_query.upper())

    if match:
        base = match.group(1)
        quote = match.group(2)
        return f"{base}/{quote}"

    # Default fallback
    return "EUR/USD"
