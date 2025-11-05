"""LangGraph workflow builder for forex trading system."""

from langgraph.graph import StateGraph, END
from graph.state import ForexAgentState
from graph.query_parser import query_parser_node
from graph.parallel_nodes import parallel_analysis_node
from graph.nodes import (
    risk_node,
    synthesis_node,
    should_continue_after_risk,
    route_after_synthesis,
)


def build_forex_workflow():
    """
    Build and compile the forex trading LangGraph workflow.

    NEW ARCHITECTURE (v2):
    1. Query Parser: Natural language → Structured JSON context
    2. Parallel Analysis: News + Technical + Fundamental (simultaneous)
    3. Risk Assessment: Validate trade parameters
    4. Conditional: If risk approved → Synthesis, else → End
    5. Synthesis: Gemini + Google Search for final decision
    6. End

    Improvements:
    - Accepts natural language queries (e.g., "Analyze gold trading")
    - 3x faster (parallel vs sequential agents)
    - Richer context passed to all agents
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

    # Set entry point - starts with query parsing
    workflow.set_entry_point("query_parser")

    # Flow: Parser → Parallel Analysis → Risk
    workflow.add_edge("query_parser", "parallel_analysis")
    workflow.add_edge("parallel_analysis", "risk")

    # Conditional edge after risk assessment
    # If risk approved, continue to synthesis
    # If risk rejected, end immediately
    workflow.add_conditional_edges(
        "risk",
        should_continue_after_risk,
        {
            "continue": "synthesis",
            "end": END,
        },
    )

    # After synthesis, always end
    # (Could add human-in-the-loop or verification here)
    workflow.add_conditional_edges(
        "synthesis",
        route_after_synthesis,
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
        print("\nWorkflow structure (v2 - with parallel execution):")
        print("  START")
        print("    ↓")
        print("  query_parser_node")
        print("    ↓")
        print("  parallel_analysis_node")
        print("    ├─ news_node")
        print("    ├─ technical_node")
        print("    └─ fundamental_node")
        print("    ↓")
        print("  risk_node")
        print("    ↓")
        print("  [Risk Approved?]")
        print("    ↓ Yes          ↓ No")
        print("  synthesis_node   END")
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
