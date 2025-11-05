"""Parallel execution node for running multiple agents simultaneously."""

import concurrent.futures
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from graph.state import ForexAgentState
from graph.nodes import news_node, technical_node, fundamental_node


def parallel_analysis_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Execute News, Technical, and Fundamental agents in parallel.

    This significantly speeds up the analysis by running all three agents
    concurrently instead of sequentially.

    Performance:
    - Sequential: ~3-6 seconds (1-2s per agent)
    - Parallel: ~1-2 seconds (max of all agents)
    - Speedup: ~3x faster

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates with all three agent results
    """
    print(f"⚡ Running parallel analysis (News + Technical + Fundamental)...")

    try:
        # Use ThreadPoolExecutor for I/O-bound tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all agents simultaneously
            news_future = executor.submit(news_node, state, config)
            technical_future = executor.submit(technical_node, state, config)
            fundamental_future = executor.submit(fundamental_node, state, config)

            # Wait for all to complete
            news_update = news_future.result()
            technical_update = technical_future.result()
            fundamental_update = fundamental_future.result()

        # Merge results
        # Note: step_count will be incremented by each agent,
        # so we take the max to avoid counting multiple times
        max_steps = max(
            news_update.get("step_count", 0),
            technical_update.get("step_count", 0),
            fundamental_update.get("step_count", 0),
        )

        # Merge errors if any
        errors = {}
        if news_update.get("errors"):
            errors.update(news_update["errors"])
        if technical_update.get("errors"):
            errors.update(technical_update["errors"])
        if fundamental_update.get("errors"):
            errors.update(fundamental_update["errors"])

        print(f"  ✅ Parallel analysis complete")

        return {
            "news_result": news_update.get("news_result"),
            "technical_result": technical_update.get("technical_result"),
            "fundamental_result": fundamental_update.get("fundamental_result"),
            "step_count": max_steps,
            "errors": errors if errors else None,
        }

    except Exception as e:
        print(f"  ❌ Parallel execution failed: {str(e)}")

        # Fall back to sequential execution
        print(f"  ⚠️  Falling back to sequential execution...")

        news_update = news_node(state, config)
        state_with_news = {**state, **news_update}

        technical_update = technical_node(state_with_news, config)
        state_with_tech = {**state_with_news, **technical_update}

        fundamental_update = fundamental_node(state_with_tech, config)

        return {
            "news_result": news_update.get("news_result"),
            "technical_result": technical_update.get("technical_result"),
            "fundamental_result": fundamental_update.get("fundamental_result"),
            "step_count": fundamental_update.get("step_count", 0),
            "errors": {**state.get("errors", {}), "parallel_execution": str(e)},
        }
