"""Streaming adapter for ForexAgentSystem to enable real-time updates."""

import json
from typing import AsyncIterator, Dict, Any
from system import ForexAgentSystem


class StreamingForexSystem:
    """
    Wrapper around ForexAgentSystem that provides streaming capabilities.

    This adapter:
    - Streams workflow execution steps in real-time
    - Provides detailed progress updates
    - Formats data for SSE (Server-Sent Events)
    - Handles errors gracefully
    """

    def __init__(self,
                 account_balance: float = None,
                 max_risk_per_trade: float = None,
                 api_key: str = None):
        """
        Initialize streaming system.

        Args:
            account_balance: Account balance in USD
            max_risk_per_trade: Max risk per trade as decimal
            api_key: Google AI API key
        """
        self.system = ForexAgentSystem(
            account_balance=account_balance,
            max_risk_per_trade=max_risk_per_trade,
            api_key=api_key
        )

    async def analyze_stream(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Analyze a trading query and stream results in real-time.

        This method streams events as the workflow progresses:
        1. Query parsing
        2. Agent analysis (News, Technical, Fundamental)
        3. Risk assessment
        4. Final synthesis

        Args:
            query: Natural language query or currency pair

        Yields:
            Dict events with type and data:
            - {"type": "start", "data": {"query": "..."}}
            - {"type": "query_parsed", "data": {...}}
            - {"type": "agent_update", "data": {...}}
            - {"type": "risk_update", "data": {...}}
            - {"type": "decision", "data": {...}}
            - {"type": "complete", "data": {...}}
            - {"type": "error", "data": {"error": "..."}}
        """
        try:
            # Send start event
            yield {
                "type": "start",
                "data": {
                    "query": query,
                    "timestamp": self._get_timestamp()
                }
            }

            # Prepare initial state
            inputs = {
                "user_query": query,
                "query_context": None,
                "pair": None,
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

            # Track previous state to detect changes
            prev_state = {}

            # Stream through the workflow
            for state in self.system.app.stream(inputs, stream_mode="values"):
                step = state.get("step_count", 0)

                # Query parsing completed
                if state.get("query_context") and not prev_state.get("query_context"):
                    yield {
                        "type": "query_parsed",
                        "data": {
                            "step": step,
                            "query_context": state["query_context"],
                            "pair": state.get("pair"),
                            "timestamp": self._get_timestamp()
                        }
                    }

                # News agent completed
                if state.get("news_result") and not prev_state.get("news_result"):
                    yield {
                        "type": "agent_update",
                        "data": {
                            "step": step,
                            "agent": "news",
                            "result": state["news_result"],
                            "timestamp": self._get_timestamp()
                        }
                    }

                # Technical agent completed
                if state.get("technical_result") and not prev_state.get("technical_result"):
                    yield {
                        "type": "agent_update",
                        "data": {
                            "step": step,
                            "agent": "technical",
                            "result": state["technical_result"],
                            "timestamp": self._get_timestamp()
                        }
                    }

                # Fundamental agent completed
                if state.get("fundamental_result") and not prev_state.get("fundamental_result"):
                    yield {
                        "type": "agent_update",
                        "data": {
                            "step": step,
                            "agent": "fundamental",
                            "result": state["fundamental_result"],
                            "timestamp": self._get_timestamp()
                        }
                    }

                # Risk assessment completed
                if state.get("risk_result") and not prev_state.get("risk_result"):
                    risk_data = state["risk_result"]
                    yield {
                        "type": "risk_update",
                        "data": {
                            "step": step,
                            "risk_result": risk_data,
                            "trade_approved": risk_data.get("data", {}).get("trade_approved", False),
                            "timestamp": self._get_timestamp()
                        }
                    }

                # Decision made
                if state.get("decision") and not prev_state.get("decision"):
                    yield {
                        "type": "decision",
                        "data": {
                            "step": step,
                            "decision": state["decision"],
                            "timestamp": self._get_timestamp()
                        }
                    }

                prev_state = state.copy()

            # Send completion event with full result
            final_result = self.system._format_result(prev_state)
            yield {
                "type": "complete",
                "data": {
                    "result": final_result,
                    "timestamp": self._get_timestamp()
                }
            }

        except Exception as e:
            # Send error event
            yield {
                "type": "error",
                "data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": self._get_timestamp()
                }
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def get_info(self) -> Dict[str, Any]:
        """Get system information."""
        return self.system.get_info()
