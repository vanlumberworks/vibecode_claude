"""Risk Agent - Calculates position sizing and risk parameters with LLM analysis."""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime


class RiskAgent:
    """
    Calculates risk management parameters for trades with intelligent LLM analysis.

    Now powered by:
    - Rule-based position sizing calculations (mathematical)
    - Gemini LLM for risk assessment and market context
    - Google Search for market conditions and volatility data
    - Structured JSON output for better LangGraph integration

    Architecture:
    1. Calculate position size, stop loss, risk/reward (rule-based)
    2. Use Gemini to analyze risk factors and market conditions
    3. Generate comprehensive risk assessment
    4. Return structured JSON with recommendations
    """

    def __init__(self, account_balance: float = 10000.0, max_risk_per_trade: float = 0.02, use_llm: bool = True):
        """
        Initialize Risk Agent.

        Args:
            account_balance: Total account balance
            max_risk_per_trade: Maximum risk per trade as decimal (e.g., 0.02 = 2%)
            use_llm: Whether to use LLM for enhanced risk analysis
        """
        self.name = "RiskAgent"
        self.account_balance = account_balance
        self.max_risk_per_trade = max_risk_per_trade
        self.use_llm = use_llm

    async def analyze(
        self,
        pair: str,
        entry_price: float,
        stop_loss: float,
        direction: str,
        take_profit: float = None,
        leverage: float = 1.0,
        market_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate risk parameters for a trade with optional LLM analysis.

        Args:
            pair: Currency pair (e.g., "EUR/USD")
            entry_price: Proposed entry price
            stop_loss: Stop loss price
            direction: "BUY" or "SELL"
            take_profit: Take profit price (optional)
            leverage: Leverage to use (default 1.0 = no leverage)
            market_context: Optional context from other agents (news, technical, fundamental)

        Returns:
            Dict with structured risk analysis results
        """
        try:
            # Always perform rule-based calculations first
            risk_calc = self._calculate_risk_params(pair, entry_price, stop_loss, direction, take_profit, leverage)

            if self.use_llm and market_context:
                # Enhance with LLM analysis
                return await self._analyze_with_llm(pair, risk_calc, market_context)
            else:
                # Return rule-based analysis only
                return risk_calc

        except Exception as e:
            print(f"  ⚠️  Risk Agent error: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _calculate_risk_params(
        self,
        pair: str,
        entry_price: float,
        stop_loss: float,
        direction: str,
        take_profit: float,
        leverage: float,
    ) -> Dict[str, Any]:
        """Calculate risk parameters using rule-based approach."""
        # Calculate risk per pip
        risk_in_pips = self._calculate_pips(entry_price, stop_loss, direction)

        # Calculate position size
        position_size = self._calculate_position_size(risk_in_pips, pair)

        # Calculate dollar risk
        dollar_risk = self.account_balance * self.max_risk_per_trade

        # Calculate reward if take profit provided
        reward_data = {}
        risk_reward_ratio = None
        if take_profit:
            reward_in_pips = self._calculate_pips(entry_price, take_profit, direction, reward=True)
            risk_reward_ratio = reward_in_pips / risk_in_pips if risk_in_pips > 0 else 0
            potential_profit = (reward_in_pips / risk_in_pips) * dollar_risk if risk_in_pips > 0 else 0

            reward_data = {
                "take_profit": take_profit,
                "reward_in_pips": round(reward_in_pips, 1),
                "risk_reward_ratio": round(risk_reward_ratio, 2),
                "potential_profit": round(potential_profit, 2),
            }

        # Validate trade
        trade_approved, rejection_reason = self._validate_trade(risk_in_pips, risk_reward_ratio)

        return {
            "success": True,
            "agent": self.name,
            "data": {
                "pair": pair,
                "direction": direction,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "risk_in_pips": round(risk_in_pips, 1),
                "position_size": round(position_size, 2),
                "dollar_risk": round(dollar_risk, 2),
                "risk_percentage": round(self.max_risk_per_trade * 100, 2),
                "leverage": leverage,
                "account_balance": self.account_balance,
                **reward_data,
                "trade_approved": trade_approved,
                "rejection_reason": rejection_reason,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "summary": self._generate_summary(trade_approved, position_size, dollar_risk, rejection_reason),
                "data_source": "rule_based",
            },
        }

    async def _analyze_with_llm(
        self,
        pair: str,
        risk_calc: Dict[str, Any],
        market_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Enhance risk analysis with Gemini LLM for market context and risk factors."""
        from google import genai
        from google.genai import types

        # Get API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            # Fallback to rule-based if no API key
            return risk_calc

        # Initialize Gemini
        client = genai.Client(api_key=api_key)

        # Build risk analysis prompt
        prompt = self._build_risk_prompt(pair, risk_calc, market_context)

        # Configure Gemini with optional Google Search
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        config = types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            tools=[grounding_tool],
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        try:
            # Generate enhanced risk analysis
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=config
            )

            # Parse LLM analysis
            llm_analysis = json.loads(response.text)

            # Extract grounding if available
            sources = []
            search_queries = []
            if response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata
                search_queries = metadata.web_search_queries or []
                if metadata.grounding_chunks:
                    sources = [{"title": c.web.title, "url": c.web.uri} for c in metadata.grounding_chunks]

            # Merge rule-based calculations with LLM insights
            risk_data = risk_calc["data"]
            risk_data.update({
                # LLM-enhanced fields
                "risk_factors": llm_analysis.get("risk_factors", []),
                "market_volatility": llm_analysis.get("market_volatility", "unknown"),
                "volatility_assessment": llm_analysis.get("volatility_assessment", ""),
                "recommended_action": llm_analysis.get("recommended_action", risk_data.get("trade_approved", False)),
                "confidence_score": llm_analysis.get("confidence_score", 0.5),
                "risk_warnings": llm_analysis.get("risk_warnings", []),
                "optimal_position_size": llm_analysis.get("optimal_position_size", risk_data["position_size"]),
                "suggested_adjustments": llm_analysis.get("suggested_adjustments", {}),
                # LLM reasoning
                "llm_analysis": llm_analysis.get("analysis", ""),
                "reasoning": llm_analysis.get("reasoning", ""),
                # Metadata
                "data_source": "llm_enhanced",
                "search_queries": search_queries,
                "sources": sources,
            })

            return {
                "success": True,
                "agent": self.name,
                "data": risk_data,
            }

        except Exception as e:
            print(f"  ⚠️  LLM risk analysis failed: {str(e)}, using rule-based")
            return risk_calc

    def _calculate_pips(self, entry: float, exit: float, direction: str, reward: bool = False) -> float:
        """Calculate pip distance between two prices."""
        # For most pairs, 1 pip = 0.0001
        # For JPY pairs, 1 pip = 0.01
        pip_multiplier = 10000  # Standard pairs
        # TODO: Detect JPY pairs and use 100 instead

        if direction == "BUY":
            if reward:
                return abs(exit - entry) * pip_multiplier
            else:
                return abs(entry - exit) * pip_multiplier
        else:  # SELL
            if reward:
                return abs(entry - exit) * pip_multiplier
            else:
                return abs(exit - entry) * pip_multiplier

    def _calculate_position_size(self, risk_in_pips: float, pair: str) -> float:
        """
        Calculate position size in lots.

        Formula: Position Size = (Account Risk) / (Risk in Pips * Pip Value)
        """
        # Standard lot = 100,000 units
        # Pip value for standard lot on EUR/USD = $10
        # We'll calculate position size in standard lots

        dollar_risk = self.account_balance * self.max_risk_per_trade
        pip_value_per_standard_lot = 10  # USD

        if risk_in_pips <= 0:
            return 0.0

        # Position size in standard lots
        position_size = dollar_risk / (risk_in_pips * pip_value_per_standard_lot)

        return position_size

    def _validate_trade(self, risk_in_pips: float, risk_reward_ratio: float = None) -> tuple:
        """
        Validate if trade meets risk management criteria.

        Returns:
            (approved: bool, reason: str or None)
        """
        # Rule 1: Risk must be positive
        if risk_in_pips <= 0:
            return False, "Invalid stop loss: risk in pips must be positive"

        # Rule 2: Risk must not be too large (e.g., max 100 pips)
        if risk_in_pips > 100:
            return False, f"Risk too high: {risk_in_pips:.1f} pips exceeds maximum of 100 pips"

        # Rule 3: Risk/Reward ratio must be at least 1.5:1 if provided
        if risk_reward_ratio is not None:
            if risk_reward_ratio < 1.5:
                return False, f"Poor risk/reward ratio: {risk_reward_ratio:.2f} is below minimum of 1.5"

        # Rule 4: Risk must not be too small (e.g., min 10 pips)
        if risk_in_pips < 10:
            return False, f"Risk too small: {risk_in_pips:.1f} pips is below minimum of 10 pips"

        return True, None

    def _generate_summary(self, approved: bool, position_size: float, dollar_risk: float, reason: str = None) -> str:
        """Generate risk analysis summary."""
        if not approved:
            return f"Trade REJECTED: {reason}"

        return f"Trade APPROVED: Position size {position_size:.2f} lots, risking ${dollar_risk:.2f} ({self.max_risk_per_trade*100:.1f}% of account)."

    def _build_risk_prompt(self, pair: str, risk_calc: Dict[str, Any], market_context: Dict[str, Any]) -> str:
        """Build the risk analysis prompt for Gemini."""

        risk_data = risk_calc["data"]

        # Extract market context
        news_sentiment = "unknown"
        technical_signals = "unknown"
        fundamental_outlook = "unknown"

        if market_context:
            if "news_result" in market_context:
                news_sentiment = market_context["news_result"].get("data", {}).get("overall_sentiment", "unknown")

            if "technical_result" in market_context:
                tech_data = market_context["technical_result"].get("data", {})
                technical_signals = tech_data.get("signals", {}).get("overall", "unknown")

            if "fundamental_result" in market_context:
                fund_data = market_context["fundamental_result"].get("data", {})
                fundamental_outlook = fund_data.get("outlook", "unknown")

        return f"""You are an expert risk management analyst for forex, commodities, and cryptocurrency trading.

TASK: Analyze risk parameters for a proposed {risk_data['direction']} trade on {pair}

PROPOSED TRADE:
- Pair: {pair}
- Direction: {risk_data['direction']}
- Entry Price: ${risk_data['entry_price']}
- Stop Loss: ${risk_data['stop_loss']}
- Take Profit: ${risk_data.get('take_profit', 'Not set')}
- Risk in Pips: {risk_data['risk_in_pips']}
- Position Size: {risk_data['position_size']} lots
- Dollar Risk: ${risk_data['dollar_risk']} ({risk_data['risk_percentage']}% of account)
- Risk/Reward Ratio: {risk_data.get('risk_reward_ratio', 'N/A')}
- Rule-Based Approval: {risk_data['trade_approved']}
- Rejection Reason: {risk_data.get('rejection_reason', 'N/A')}

MARKET CONTEXT:
- News Sentiment: {news_sentiment}
- Technical Signals: {technical_signals}
- Fundamental Outlook: {fundamental_outlook}

ACCOUNT PARAMETERS:
- Account Balance: ${risk_data['account_balance']}
- Max Risk per Trade: {risk_data['risk_percentage']}%
- Leverage: {risk_data['leverage']}x

ANALYSIS REQUIREMENTS:

1. **Risk Factors Analysis** (Use Google Search for current market conditions)
   Identify 3-5 key risk factors affecting this trade:
   - Market volatility (current ATR, recent price swings)
   - Economic events scheduled (rate decisions, data releases)
   - Geopolitical factors
   - Liquidity conditions
   - Correlation risks
   - Technical support/resistance levels near stop loss

2. **Market Volatility Assessment**
   Classify current market volatility for {pair}:
   - "low" (< 0.5% daily moves)
   - "medium" (0.5-1.5% daily moves)
   - "high" (> 1.5% daily moves)

   Provide assessment explaining:
   - Current Average True Range (ATR)
   - Recent volatility patterns
   - Whether stop loss is appropriate for current volatility

3. **Position Size Validation**
   Evaluate if proposed position size {risk_data['position_size']} lots is optimal:
   - Is it appropriate for current volatility?
   - Should it be reduced/increased based on market conditions?
   - Does it align with news sentiment and technical signals?

4. **Risk Warnings**
   List specific warnings for this trade:
   - Conflicting signals (e.g., bullish technical but bearish news)
   - High-impact events coming up
   - Stop loss too tight/too wide
   - Poor risk/reward ratio
   - High leverage concerns

5. **Recommended Action**
   - true: Trade is acceptable with current parameters
   - false: Trade should be avoided or parameters adjusted

6. **Confidence Score** (0.0 to 1.0)
   How confident are you in this risk assessment?
   - 0.0-0.3: Low confidence (conflicting signals, high uncertainty)
   - 0.4-0.6: Medium confidence (some uncertainty remains)
   - 0.7-1.0: High confidence (clear risk profile)

7. **Suggested Adjustments**
   If parameters need adjustment, provide specific recommendations:
   - Optimal position size (lots)
   - Better stop loss level
   - Better take profit level
   - Timing suggestions (wait for event, enter after breakout, etc.)

OUTPUT FORMAT (JSON):
{{
  "risk_factors": [
    "High volatility due to upcoming Fed decision",
    "Technical stop loss near key support level",
    "News sentiment bearish contradicts bullish technical signal",
    "Low liquidity expected during Asian session",
    "EUR/GBP correlation risk"
  ],
  "market_volatility": "high",
  "volatility_assessment": "Current ATR for {pair} is 85 pips (20-day), well above the 50-pip average. This suggests elevated risk. The proposed 35-pip stop loss may be too tight given current volatility. Recommend widening to 60-70 pips or reducing position size by 40%.",
  "recommended_action": true,
  "confidence_score": 0.75,
  "risk_warnings": [
    "FOMC meeting in 2 days - expect increased volatility",
    "Stop loss at ${{risk_data['stop_loss']}} is only 5 pips from recent swing low - may get stopped out prematurely",
    "Risk/reward ratio of {{risk_data.get('risk_reward_ratio', 'N/A')}} is below optimal 2:1",
    "High leverage of {{risk_data['leverage']}}x amplifies risk in volatile conditions"
  ],
  "optimal_position_size": 0.15,
  "suggested_adjustments": {{
    "position_size": 0.15,
    "stop_loss": {{risk_data['stop_loss']}} - 0.0020,
    "take_profit": {{risk_data['entry_price']}} + 0.0140,
    "timing": "Wait for FOMC meeting to pass, or enter half position now and add after event"
  }},
  "analysis": "Risk analysis for {pair} {risk_data['direction']} trade shows elevated volatility conditions with upcoming Fed decision. Position size of {risk_data['position_size']} lots risking ${risk_data['dollar_risk']} is within acceptable limits but stop loss placement is suboptimal given current ATR. Market conditions favor a more conservative approach.",
  "reasoning": "Recommended to proceed with reduced position size (0.15 lots instead of {risk_data['position_size']}) due to: 1) High volatility environment (85 pips ATR vs 50 avg), 2) Conflicting news sentiment ({news_sentiment}) versus technical signals ({technical_signals}), 3) Upcoming high-impact event creating uncertainty. Stop loss should be widened to account for volatility or position size reduced to maintain same dollar risk.",
  "summary": "Trade acceptable with adjustments: Reduce position to 0.15 lots OR widen stop loss to 60 pips. Consider waiting for FOMC meeting to pass. Risk/reward profile improves with adjusted parameters."
}}

CRITICAL:
- Use REAL market data from Google Search for volatility and event calendar
- Be objective and data-driven - prioritize capital preservation
- If conflicting signals exist, recommend caution
- Consider the trader's account size and risk tolerance
- Recent market volatility trumps historical patterns

Analyze now: {pair} {risk_data['direction']} trade with {risk_data['position_size']} lots risking ${risk_data['dollar_risk']}
"""
