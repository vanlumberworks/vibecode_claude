"""State definition for LangGraph forex agent system."""

from typing import Annotated, Sequence, TypedDict, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ForexAgentState(TypedDict):
    """
    State for multi-agent forex analysis using LangGraph.

    This state is passed through the graph and updated by each node.
    """

    # Conversation history (optional, for chat-like interface)
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Raw user input
    user_query: str  # e.g., "Analyze gold trading", "What about EUR/USD?"

    # Parsed query context (from query parser node)
    query_context: Optional[Dict[str, Any]]
    # Structure:
    # {
    #   "pair": "XAU/USD",
    #   "asset_type": "commodity",
    #   "base_currency": "XAU",
    #   "quote_currency": "USD",
    #   "timeframe": "intraday",
    #   "user_intent": "trading_signal",
    #   "risk_tolerance": "moderate",
    #   "additional_context": {...}
    # }

    # Deprecated: kept for backwards compatibility
    pair: Optional[str]  # e.g., "EUR/USD"

    # Agent results
    news_result: Optional[Dict[str, Any]]
    technical_result: Optional[Dict[str, Any]]
    fundamental_result: Optional[Dict[str, Any]]
    risk_result: Optional[Dict[str, Any]]

    # Final decision from synthesis
    decision: Optional[Dict[str, Any]]

    # Metadata
    step_count: int
    should_continue: bool

    # Error tracking
    errors: Optional[Dict[str, str]]
