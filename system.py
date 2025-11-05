"""Forex Agent System - Main orchestrator using LangGraph."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from graph.workflow import build_forex_workflow, visualize_workflow, get_workflow_info


class ForexAgentSystem:
    """
    Multi-agent forex trading system using LangGraph + Gemini.

    This system orchestrates:
    - NewsAgent: Analyzes market news and sentiment
    - TechnicalAgent: Performs technical analysis
    - FundamentalAgent: Analyzes economic fundamentals
    - RiskAgent: Calculates position sizing and risk
    - Synthesis: Gemini LLM with Google Search grounding for final decision

    Architecture:
    - LangGraph: Agent orchestration and state management
    - Gemini 2.5 Flash: LLM synthesis
    - Google Search: Real-time data grounding
    """

    def __init__(
        self,
        account_balance: Optional[float] = None,
        max_risk_per_trade: Optional[float] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Forex Agent System.

        Args:
            account_balance: Account balance in USD (default: from env or 10000)
            max_risk_per_trade: Max risk per trade as decimal (default: from env or 0.02)
            api_key: Google AI API key (default: from env)
        """
        # Load environment variables
        load_dotenv()

        # Set account parameters
        if account_balance is not None:
            os.environ["ACCOUNT_BALANCE"] = str(account_balance)
        elif "ACCOUNT_BALANCE" not in os.environ:
            os.environ["ACCOUNT_BALANCE"] = "10000.0"

        if max_risk_per_trade is not None:
            os.environ["MAX_RISK_PER_TRADE"] = str(max_risk_per_trade)
        elif "MAX_RISK_PER_TRADE" not in os.environ:
            os.environ["MAX_RISK_PER_TRADE"] = "0.02"

        # Set API key
        if api_key is not None:
            os.environ["GOOGLE_AI_API_KEY"] = api_key

        # Validate API key exists
        if not os.getenv("GOOGLE_AI_API_KEY"):
            raise ValueError(
                "GOOGLE_AI_API_KEY not found. "
                "Please set it in .env file or pass as argument. "
                "Get your key from: https://aistudio.google.com/app/apikey"
            )

        # Build workflow
        self.app = build_forex_workflow()

        print("✅ Forex Agent System initialized")
        print(f"   Account Balance: ${os.getenv('ACCOUNT_BALANCE')}")
        print(f"   Max Risk Per Trade: {float(os.getenv('MAX_RISK_PER_TRADE'))*100}%")

    def analyze(self, query: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Analyze a trading query and make a decision.

        NEW: Now accepts natural language queries!
        - "Analyze gold trading"
        - "Should I buy EUR/USD?"
        - "What about Bitcoin?"
        - "EUR/USD" (still works)

        This method:
        1. Parses natural language query into structured context
        2. Runs analysis agents in parallel (News, Technical, Fundamental)
        3. Validates risk parameters
        4. Synthesizes results using Gemini + Google Search
        5. Returns a trading decision with citations

        Args:
            query: Natural language query or currency pair
                   Examples: "Analyze gold", "EUR/USD", "Should I buy Bitcoin?"
            verbose: Print progress messages (default: True)

        Returns:
            Dict with final decision and all agent results

        Example:
            >>> system = ForexAgentSystem()
            >>> result = system.analyze("Analyze gold trading")
            >>> print(result["decision"]["action"])  # BUY, SELL, or WAIT
            >>> print(result["query_context"]["pair"])  # XAU/USD
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"🔍 QUERY: {query}")
            print(f"{'='*60}\n")

        # Prepare initial state with natural language query
        inputs = {
            "user_query": query,
            "query_context": None,
            "pair": None,  # Will be set by query parser
            "messages": [],
            "step_count": 0,
            "news_result": None,
            "technical_result": None,
            "fundamental_result": None,
            "risk_result": None,
            "decision": None,
            "should_continue": True,
            "errors": None,
        }

        # Stream execution through the graph
        final_state = None
        for state in self.app.stream(inputs, stream_mode="values"):
            final_state = state
            if verbose:
                step = state.get("step_count", 0)
                print(f"   Step {step} completed")

        if verbose:
            print(f"\n{'='*60}")
            self._print_decision(final_state)
            print(f"{'='*60}\n")

        return self._format_result(final_state)

    def visualize(self):
        """
        Visualize the workflow graph.

        Requires: ipython, matplotlib
        """
        visualize_workflow(self.app)

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the system and workflow.

        Returns:
            Dict with system information
        """
        workflow_info = get_workflow_info(self.app)

        return {
            "system": {
                "account_balance": float(os.getenv("ACCOUNT_BALANCE", 10000)),
                "max_risk_per_trade": float(os.getenv("MAX_RISK_PER_TRADE", 0.02)),
                "api_configured": bool(os.getenv("GOOGLE_AI_API_KEY")),
            },
            "workflow": workflow_info,
        }

    def _format_result(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final state into a structured result."""
        decision = state.get("decision", {})

        # Handle case where workflow ended early (risk rejected)
        if not decision:
            risk_result = state.get("risk_result", {})
            if risk_result.get("data", {}).get("trade_approved") == False:
                decision = {
                    "action": "WAIT",
                    "confidence": 0.0,
                    "reasoning": {
                        "summary": f"Trade rejected by Risk Agent: {risk_result['data'].get('rejection_reason')}",
                        "risk_rejection": True,
                    },
                }

        return {
            "user_query": state.get("user_query"),
            "query_context": state.get("query_context"),
            "pair": state.get("pair"),
            "decision": decision,
            "agent_results": {
                "news": state.get("news_result"),
                "technical": state.get("technical_result"),
                "fundamental": state.get("fundamental_result"),
                "risk": state.get("risk_result"),
            },
            "metadata": {
                "steps": state.get("step_count", 0),
                "errors": state.get("errors"),
            },
        }

    def _print_decision(self, state: Dict[str, Any]):
        """Print the final decision in a readable format."""
        decision = state.get("decision", {})

        if not decision:
            print("⚠️  No decision made (workflow ended early)")
            risk_result = state.get("risk_result", {})
            if risk_result.get("data", {}).get("trade_approved") == False:
                print(f"   Reason: {risk_result['data'].get('rejection_reason')}")
            return

        action = decision.get("action", "UNKNOWN")
        confidence = decision.get("confidence", 0.0)

        # Print action with emoji
        action_emoji = {"BUY": "🟢", "SELL": "🔴", "WAIT": "🟡"}.get(action, "❓")

        print(f"{action_emoji} DECISION: {action}")
        print(f"   Confidence: {confidence:.0%}")

        # Print reasoning
        reasoning = decision.get("reasoning", {})
        if "summary" in reasoning:
            print(f"\n   Summary: {reasoning['summary']}")

        # Print key factors
        if "key_factors" in reasoning:
            print(f"\n   Key Factors:")
            for factor in reasoning["key_factors"]:
                print(f"     • {factor}")

        # Print trade parameters (if BUY/SELL)
        if action in ["BUY", "SELL"]:
            params = decision.get("trade_parameters", {})
            if params:
                print(f"\n   Trade Parameters:")
                print(f"     Entry: {params.get('entry_price', 'N/A')}")
                print(f"     Stop Loss: {params.get('stop_loss', 'N/A')}")
                print(f"     Take Profit: {params.get('take_profit', 'N/A')}")
                print(f"     Position Size: {params.get('position_size', 'N/A')} lots")

        # Print sources
        grounding = decision.get("grounding_metadata", {})
        sources = grounding.get("sources", [])
        if sources:
            print(f"\n   🌐 Sources ({len(sources)}):")
            for i, source in enumerate(sources[:3], 1):  # Show first 3
                print(f"     {i}. {source.get('title', 'Unknown')}")
                print(f"        {source.get('url', 'No URL')}")
