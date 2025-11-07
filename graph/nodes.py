"""LangGraph node functions for forex agent system."""

import json
import os
import time
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from graph.state import ForexAgentState
from agents import NewsAgent, TechnicalAgent, FundamentalAgent, RiskAgent
from agents.report_agent import ReportAgent
from utils.logger import get_logger, log_error

logger = get_logger(__name__)


async def news_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Analyze news for the currency pair using Google Search.

    Now async and powered by real Google Search!

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    from langgraph.config import get_stream_writer

    pair = state["pair"]
    logger.info(f"📰 [NEWS NODE] Starting analysis for {pair}")
    start_time = time.time()

    try:
        # Emit agent start event
        writer = get_stream_writer()
        writer({"agent_start": {"agent": "news", "pair": pair, "status": "starting"}})

        agent = NewsAgent()
        result = await agent.analyze(pair, config=config)

        elapsed = time.time() - start_time
        success = result.get("success", False)
        logger.info(f"📰 [NEWS NODE] Completed - Success: {success}, Time: {elapsed:.2f}s")

        return {
            "news_result": result,
            "step_count": state.get("step_count", 0) + 1,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        log_error(logger, e, "news_node")
        logger.error(f"📰 [NEWS NODE] Failed after {elapsed:.2f}s")

        return {
            "news_result": {"success": False, "error": str(e)},
            "step_count": state.get("step_count", 0) + 1,
            "errors": {**(state.get("errors") or {}), "news": str(e)},
        }


async def technical_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Perform technical analysis.

    Now async for parallel execution.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    from langgraph.config import get_stream_writer

    pair = state["pair"]
    logger.info(f"📊 [TECHNICAL NODE] Starting analysis for {pair}")
    start_time = time.time()

    try:
        # Emit agent start event
        writer = get_stream_writer()
        writer({"agent_start": {"agent": "technical", "pair": pair, "status": "starting"}})

        agent = TechnicalAgent()
        result = await agent.analyze(pair, config=config)

        elapsed = time.time() - start_time
        success = result.get("success", False)
        logger.info(f"📊 [TECHNICAL NODE] Completed - Success: {success}, Time: {elapsed:.2f}s")

        return {
            "technical_result": result,
            "step_count": state["step_count"] + 1,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        log_error(logger, e, "technical_node")
        logger.error(f"📊 [TECHNICAL NODE] Failed after {elapsed:.2f}s")

        return {
            "technical_result": {"success": False, "error": str(e)},
            "step_count": state["step_count"] + 1,
            "errors": {**(state.get("errors") or {}), "technical": str(e)},
        }


async def fundamental_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Analyze fundamental data.

    Now async for parallel execution.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    from langgraph.config import get_stream_writer

    pair = state["pair"]
    logger.info(f"💼 [FUNDAMENTAL NODE] Starting analysis for {pair}")
    start_time = time.time()

    try:
        # Emit agent start event
        writer = get_stream_writer()
        writer({"agent_start": {"agent": "fundamental", "pair": pair, "status": "starting"}})

        agent = FundamentalAgent()
        result = await agent.analyze(pair, config=config)

        elapsed = time.time() - start_time
        success = result.get("success", False)
        logger.info(f"💼 [FUNDAMENTAL NODE] Completed - Success: {success}, Time: {elapsed:.2f}s")

        return {
            "fundamental_result": result,
            "step_count": state["step_count"] + 1,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        log_error(logger, e, "fundamental_node")
        logger.error(f"💼 [FUNDAMENTAL NODE] Failed after {elapsed:.2f}s")
        return {
            "fundamental_result": {"success": False, "error": str(e)},
            "step_count": state["step_count"] + 1,
            "errors": {**(state.get("errors") or {}), "fundamental": str(e)},
        }


async def risk_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Calculate risk parameters (ADVISORY ONLY).

    Risk assessment is now advisory - failures here won't block the workflow.

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates
    """
    pair = state["pair"]
    print(f"⚖️  Risk Agent calculating parameters (advisory only)...")

    try:
        # Get technical analysis results for entry/stop prices
        ta_result = state.get("technical_result", {})
        if not ta_result.get("success"):
            # If technical analysis failed, return advisory-only result
            print("⚠️  Technical analysis failed - risk assessment unavailable (advisory only)")
            return {
                "risk_result": {
                    "success": False,
                    "error": "Technical analysis required for risk calculation",
                    "data": {"trade_approved": False, "rejection_reason": "Technical analysis unavailable"},
                },
                "step_count": state["step_count"] + 1,
            }

        ta_data = ta_result["data"]
        current_price = ta_data.get("current_price")
        stop_loss = ta_data.get("stop_loss")

        # Validate required data
        if not current_price or not stop_loss:
            print("⚠️  Missing price/stop loss - risk assessment unavailable (advisory only)")
            return {
                "risk_result": {
                    "success": False,
                    "error": "Missing required price data",
                    "data": {"trade_approved": False, "rejection_reason": "Incomplete technical data"},
                },
                "step_count": state["step_count"] + 1,
            }

        # Determine direction from technical signals
        signals = ta_data.get("signals", {})
        direction = "BUY" if signals.get("overall") == "BUY" else "SELL"

        # Get take profit
        take_profit = ta_data.get("take_profit")

        # Get account settings from environment or use defaults
        account_balance = float(os.getenv("ACCOUNT_BALANCE", "10000.0"))
        max_risk = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))

        # Initialize risk agent
        agent = RiskAgent(account_balance=account_balance, max_risk_per_trade=max_risk)

        # Analyze risk
        result = await agent.analyze(
            pair=pair, entry_price=current_price, stop_loss=stop_loss, direction=direction, take_profit=take_profit, leverage=1.0
        )

        return {
            "risk_result": result,
            "step_count": state["step_count"] + 1,
        }
    except Exception as e:
        print(f"⚠️  Risk calculation error: {str(e)} (advisory only)")
        return {
            "risk_result": {
                "success": False,
                "error": str(e),
                "data": {"trade_approved": False, "rejection_reason": f"Risk calculation error: {str(e)}"},
            },
            "step_count": state["step_count"] + 1,
            "errors": {**(state.get("errors") or {}), "risk": str(e)},
        }


def synthesis_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Synthesize all agent outputs using Gemini LLM.

    This is the critical node where:
    1. All agent outputs are collected
    2. Gemini LLM synthesizes the information
    3. Risk assessment is considered as advisory
    4. Final trading decision is made with clear reasoning

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates with final decision
    """
    from langgraph.config import get_stream_writer

    pair = state["pair"]
    print(f"🤖 Synthesis Agent making final decision...")

    try:
        # Get stream writer for progress updates
        writer = get_stream_writer()
        writer({"agent_progress": {"agent": "synthesis", "step": "collecting_data", "message": "Collecting all agent results"}})

        from google import genai
        from google.genai import types

        # Emit progress: Building synthesis
        writer({"agent_progress": {"agent": "synthesis", "step": "building_synthesis", "message": "Building comprehensive analysis"}})


        # Initialize Gemini client
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found in environment")

        client = genai.Client(api_key=api_key)

        # Build comprehensive prompt
        prompt = _build_synthesis_prompt(state)

        # Configure without Google Search (to avoid API conflicts with JSON response)
        config_gemini = types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disable thinking for speed
        )

        # Emit progress: Analyzing
        writer({"agent_progress": {"agent": "synthesis", "step": "analyzing", "message": "Analyzing all agent data for final decision"}})

        # Generate decision
        response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt], config=config_gemini)

        # Emit progress: Processing decision
        writer({"agent_progress": {"agent": "synthesis", "step": "processing_decision", "message": "Processing final trading decision"}})

        # Parse decision
        decision = json.loads(response.text)

        print(f"✅ Final decision: {decision.get('action', 'UNKNOWN')}")

        return {
            "decision": decision,
            "step_count": state["step_count"] + 1,
        }

    except Exception as e:
        print(f"❌ Synthesis failed: {str(e)}")
        # Fallback decision
        return {
            "decision": {
                "action": "WAIT",
                "confidence": 0.0,
                "reasoning": {"summary": f"Synthesis failed: {str(e)}", "error": True},
            },
            "step_count": state["step_count"] + 1,
            "errors": {**(state.get("errors") or {}), "synthesis": str(e)},
        }


def _build_synthesis_prompt(state: ForexAgentState) -> str:
    """Build the synthesis prompt for Gemini."""
    pair = state["pair"]

    # Extract agent results
    news_data = state.get("news_result", {}).get("data", {})
    tech_data = state.get("technical_result", {}).get("data", {})
    fund_data = state.get("fundamental_result", {}).get("data", {})
    risk_data = state.get("risk_result", {}).get("data", {})

    prompt = f"""You are an expert forex trading synthesizer. Analyze the following agent data to make a final trading decision.

CURRENCY PAIR: {pair}

AGENT ANALYSIS:

📰 NEWS AGENT:
{json.dumps(news_data, indent=2)}

📊 TECHNICAL AGENT:
{json.dumps(tech_data, indent=2)}

💰 FUNDAMENTAL AGENT:
{json.dumps(fund_data, indent=2)}

⚖️  RISK AGENT (ADVISORY ONLY):
{json.dumps(risk_data, indent=2)}

TASK:
1. Analyze all agent outputs comprehensively
2. Consider alignment/conflicts between agents (news vs technical vs fundamental)
3. Synthesize all information into a final trading decision
4. Provide clear reasoning and actionable recommendations

CRITICAL RULES:
- Risk Agent assessment is ADVISORY ONLY - consider it but don't let it block decisions
- If Risk Agent flagged concerns, note them in reasoning but still make a decision based on market analysis
- Consider all three dimensions: news sentiment, technical signals, fundamentals
- Only recommend BUY/SELL if confidence is high (>0.7) based on market analysis
- When agents conflict, explain which factors you weighted more heavily and why
- Include disclaimer: "Risk assessment is for informational purposes only"

OUTPUT FORMAT (JSON):
{{
  "action": "BUY|SELL|WAIT",
  "confidence": 0.0-1.0,
  "reasoning": {{
    "summary": "One paragraph summary of the decision",
    "web_verification": "What real-time data confirmed or contradicted the mock analysis",
    "key_factors": ["factor1", "factor2", "factor3"],
    "risks": ["risk1", "risk2"],
    "risk_advisory": "Note any concerns from Risk Agent if trade_approved=false"
  }},
  "trade_parameters": {{
    "entry_price": {tech_data.get('current_price', 0)},
    "stop_loss": {tech_data.get('stop_loss', 0)},
    "take_profit": {tech_data.get('take_profit', 0)},
    "position_size": {risk_data.get('position_size', 0)}
  }},
  "disclaimer": "Risk assessment and position sizing are for informational purposes only. Always conduct your own research and consult with a financial advisor before trading."
}}

Remember: Be conservative. When in doubt, output "WAIT".
"""

    return prompt


async def report_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Node: Generate comprehensive PDF-ready HTML report.

    This node uses Gemini to create narrative sections and assembles
    them into a professional HTML document with all analysis results.

    Args:
        state: Current graph state with all analysis results
        config: Runtime configuration

    Returns:
        State updates with report_result
    """
    from langgraph.config import get_stream_writer

    pair = state["pair"]
    print(f"📄 Report Agent generating comprehensive report...")

    try:
        # Get stream writer for progress updates
        writer = get_stream_writer()
        writer({"agent_start": {"agent": "report", "pair": pair, "status": "starting"}})

        # Emit progress: Collecting data
        writer({"agent_progress": {"agent": "report", "step": "collecting_data", "message": "Collecting all analysis results"}})

        # Initialize Report Agent
        agent = ReportAgent()

        # Get all required data from state
        decision = state.get("decision", {})
        query_context = state.get("query_context", {})
        news_result = state.get("news_result", {})
        technical_result = state.get("technical_result", {})
        fundamental_result = state.get("fundamental_result", {})
        risk_result = state.get("risk_result", {})

        # Emit progress: Generating content
        writer({"agent_progress": {"agent": "report", "step": "generating_content", "message": "Generating report sections with LLM"}})

        # Generate report
        result = await agent.generate_report(
            decision=decision,
            query_context=query_context,
            pair=pair,
            news_result=news_result,
            technical_result=technical_result,
            fundamental_result=fundamental_result,
            risk_result=risk_result,
        )

        # Emit progress: Assembling HTML
        writer({"agent_progress": {"agent": "report", "step": "assembling_html", "message": "Assembling PDF-ready HTML"}})

        success = result.get("success", False)
        if success:
            print(f"✅ Report generated successfully ({result.get('metadata', {}).get('word_count', 0)} words)")
        else:
            print(f"⚠️  Report generation failed: {result.get('error', 'Unknown error')}")

        return {
            "report_result": result,
            "step_count": state["step_count"] + 1,
        }

    except Exception as e:
        print(f"❌ Report generation error: {str(e)}")
        return {
            "report_result": {
                "success": False,
                "agent": "ReportAgent",
                "error": str(e),
                "html": None,
            },
            "step_count": state["step_count"] + 1,
            "errors": {**(state.get("errors") or {}), "report": str(e)},
        }


# Conditional edge functions
def should_continue_after_risk(state: ForexAgentState) -> str:
    """
    Determine if we should continue to synthesis after risk analysis.

    IMPORTANT: Risk is now ADVISORY ONLY - we always continue to synthesis.
    The synthesis agent will consider risk assessment but won't be blocked by it.
    """
    risk_result = state.get("risk_result", {})

    if not risk_result.get("success", False):
        print("⚠️  Risk analysis failed, but continuing (risk is advisory only)")
        return "continue"

    risk_data = risk_result.get("data", {})
    if not risk_data.get("trade_approved", False):
        print(f"⚠️  Trade flagged by Risk Agent: {risk_data.get('rejection_reason')}")
        print("   (Risk is advisory only - continuing to synthesis)")
        return "continue"

    print("✅ Risk approved, proceeding to synthesis")
    return "continue"


def route_after_synthesis(state: ForexAgentState) -> str:
    """
    Route after synthesis node.

    Now routes to report generation for comprehensive HTML output.
    """
    decision = state.get("decision", {})
    action = decision.get("action", "WAIT")

    print(f"🎯 Routing after synthesis: {action} → Generating report")
    return "report"


def route_after_report(state: ForexAgentState) -> str:
    """
    Route after report generation node.

    Report is always the last step, so we end the workflow.
    """
    report_result = state.get("report_result", {})
    success = report_result.get("success", False)

    print(f"🎯 Routing after report: {'Success' if success else 'Failed'} → End")
    return "end"
