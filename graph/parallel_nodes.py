"""Parallel execution node for running multiple agents simultaneously using asyncio."""

import asyncio
import time
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from graph.state import ForexAgentState
from graph.nodes import news_node, technical_node, fundamental_node
from utils.logger import get_logger, log_error

logger = get_logger(__name__)


async def parallel_analysis_node(state: ForexAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Execute News, Technical, and Fundamental agents in parallel using asyncio.

    This significantly speeds up the analysis by running all three agents
    concurrently instead of sequentially.

    Performance:
    - Sequential: ~3-6 seconds (1-2s per agent)
    - Parallel (async): ~1-2 seconds (max of all agents)
    - Speedup: ~3x faster

    Args:
        state: Current graph state
        config: Runtime configuration

    Returns:
        State updates with all three agent results
    """
    pair = state.get("pair", "UNKNOWN")
    logger.info(f"⚡ [PARALLEL NODE] Starting parallel analysis for {pair}")
    logger.info("⚡ [PARALLEL NODE] Launching 3 agents concurrently: News, Technical, Fundamental")
    start_time = time.time()

    try:
        # Run all agents concurrently with asyncio.gather()
        results = await asyncio.gather(
            news_node(state, config),
            technical_node(state, config),
            fundamental_node(state, config),
            return_exceptions=True  # Don't fail entire operation if one agent fails
        )

        elapsed = time.time() - start_time
        logger.info(f"⚡ [PARALLEL NODE] All agents completed in {elapsed:.2f}s")

        news_update, technical_update, fundamental_update = results

        # Handle exceptions from individual agents
        if isinstance(news_update, Exception):
            print(f"  ⚠️  News agent failed: {str(news_update)}")
            news_update = {
                "news_result": {"success": False, "error": str(news_update)},
                "step_count": state.get("step_count", 0) + 1,
                "errors": {"news": str(news_update)},
            }

        if isinstance(technical_update, Exception):
            print(f"  ⚠️  Technical agent failed: {str(technical_update)}")
            technical_update = {
                "technical_result": {"success": False, "error": str(technical_update)},
                "step_count": state.get("step_count", 0) + 1,
                "errors": {"technical": str(technical_update)},
            }

        if isinstance(fundamental_update, Exception):
            print(f"  ⚠️  Fundamental agent failed: {str(fundamental_update)}")
            fundamental_update = {
                "fundamental_result": {"success": False, "error": str(fundamental_update)},
                "step_count": state.get("step_count", 0) + 1,
                "errors": {"fundamental": str(fundamental_update)},
            }

        # Merge results
        # Note: step_count will be incremented by each agent,
        # so we take the max to avoid counting multiple times
        max_steps = max(
            news_update.get("step_count", 0) if isinstance(news_update, dict) else 0,
            technical_update.get("step_count", 0) if isinstance(technical_update, dict) else 0,
            fundamental_update.get("step_count", 0) if isinstance(fundamental_update, dict) else 0,
        )

        # Merge errors if any
        errors = {}
        if isinstance(news_update, dict) and news_update.get("errors"):
            if isinstance(news_update["errors"], dict):
                errors.update(news_update["errors"])
        if isinstance(technical_update, dict) and technical_update.get("errors"):
            if isinstance(technical_update["errors"], dict):
                errors.update(technical_update["errors"])
        if isinstance(fundamental_update, dict) and fundamental_update.get("errors"):
            if isinstance(fundamental_update["errors"], dict):
                errors.update(fundamental_update["errors"])

        logger.info(f"✅ [PARALLEL NODE] Parallel analysis complete - All 3 agents finished")
        logger.debug(f"⚡ [PARALLEL NODE] Results: News={news_update is not Exception}, Tech={technical_update is not Exception}, Fund={fundamental_update is not Exception}")

        return {
            "news_result": news_update.get("news_result"),
            "technical_result": technical_update.get("technical_result"),
            "fundamental_result": fundamental_update.get("fundamental_result"),
            "step_count": max_steps,
            "errors": errors if errors else None,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        log_error(logger, e, "parallel_analysis_node")
        logger.error(f"❌ [PARALLEL NODE] Async parallel execution failed after {elapsed:.2f}s")

        # Fall back to sequential execution
        logger.warning(f"⚠️  [PARALLEL NODE] Falling back to sequential async execution...")

        try:
            news_update = await news_node(state, config)
            state_with_news = {**state, **news_update}

            technical_update = await technical_node(state_with_news, config)
            state_with_tech = {**state_with_news, **technical_update}

            fundamental_update = await fundamental_node(state_with_tech, config)

            return {
                "news_result": news_update.get("news_result"),
                "technical_result": technical_update.get("technical_result"),
                "fundamental_result": fundamental_update.get("fundamental_result"),
                "step_count": fundamental_update.get("step_count", 0),
                "errors": {**(state.get("errors") or {}), "parallel_execution": str(e)},
            }
        except Exception as sequential_error:
            print(f"  ❌ Sequential fallback also failed: {str(sequential_error)}")
            raise
