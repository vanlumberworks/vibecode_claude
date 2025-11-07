"""LangGraph workflow builder for forex trading system."""

from langgraph.graph import StateGraph, END
from graph.state import ForexAgentState
from graph.query_parser import query_parser_node
from graph.parallel_nodes import parallel_analysis_node
from graph.nodes import (
    risk_node,
    synthesis_node,
    report_node,
    should_continue_after_risk,
    route_after_synthesis,
    route_after_report,
)


def build_forex_workflow():
    """
    Build and compile the forex trading LangGraph workflow.

    ARCHITECTURE (v2 + Report + Advisory Risk):
    1. Query Parser: Natural language → Structured JSON context
    2. Parallel Analysis: News + Technical + Fundamental (simultaneous)
    3. Risk Assessment: Advisory analysis of trade parameters (non-blocking)
    4. Synthesis: Gemini + Google Search for final decision (always runs)
    5. Report Generation: LLM-powered PDF-ready HTML report
    6. End

    Improvements:
    - Accepts natural language queries (e.g., "Analyze gold trading")
    - 3x faster (parallel vs sequential agents)
    - Richer context passed to all agents
    - Risk assessment is advisory only (won't block decisions)
    - Comprehensive HTML report generation with disclaimers
    - Better user experience

    Returns:
        Compiled StateGraph application
    """
    # Create the state graph
    workflow = StateGraph(ForexAgentState)

    # Add nodes
    workflow.add_node("query_parser", query_parser_node)
    workflow.add_node("parallel_analysis", parallel_analysis_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("report", report_node)

    # Set entry point - starts with query parsing
    workflow.set_entry_point("query_parser")

    # Flow: Parser → Parallel Analysis → Risk
    workflow.add_edge("query_parser", "parallel_analysis")
    workflow.add_edge("parallel_analysis", "risk")

    # Conditional edge after risk assessment
    # Risk is ADVISORY ONLY - always continue to synthesis
    # The synthesis agent considers risk but won't be blocked by it
    workflow.add_conditional_edges(
        "risk",
        should_continue_after_risk,
        {
            "continue": "synthesis",
            "end": END,  # Never reached - kept for API compatibility
        },
    )

    # After synthesis, route to report generation
    workflow.add_conditional_edges(
        "synthesis",
        route_after_synthesis,
        {
            "report": "report",
        },
    )

    # After report generation, always end
    workflow.add_conditional_edges(
        "report",
        route_after_report,
        {
            "end": END,
        },
    )

    # Compile the graph
    app = workflow.compile()

    return app


def visualize_workflow(app=None):
    """
    Visualize the workflow graph.

    Requires: ipython, matplotlib

    Args:
        app: Compiled workflow (if None, builds a new one)
    """
    if app is None:
        app = build_forex_workflow()

    try:
        from IPython.display import Image, display

        # Generate mermaid diagram
        png_data = app.get_graph().draw_mermaid_png()
        display(Image(png_data))
    except ImportError:
        print("Visualization requires IPython. Install with: pip install ipython")
        print("\nWorkflow structure (v2 - with parallel execution + advisory risk + report generation):")
        print("  START")
        print("    ↓")
        print("  query_parser_node")
        print("    ↓")
        print("  parallel_analysis_node")
        print("    ├─ news_node")
        print("    ├─ technical_node")
        print("    └─ fundamental_node")
        print("    ↓")
        print("  risk_node (advisory only)")
        print("    ↓")
        print("  synthesis_node")
        print("    ↓")
        print("  report_node")
        print("    ↓")
        print("  END")


def get_workflow_info(app=None):
    """
    Get information about the workflow.

    Args:
        app: Compiled workflow (if None, builds a new one)

    Returns:
        Dict with workflow information
    """
    if app is None:
        app = build_forex_workflow()

    # Get graph structure
    graph = app.get_graph()

    nodes = list(graph.nodes.keys())
    edges = [(e.source, e.target) for e in graph.edges]

    return {
        "nodes": nodes,
        "edges": edges,
        "num_nodes": len(nodes),
        "num_edges": len(edges),
    }
