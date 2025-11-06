# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LangGraph + Gemini 2.5 Flash** multi-agent forex/commodity/crypto trading analysis system. It orchestrates specialized agents to analyze trading opportunities and make decisions backed by real-time Google Search grounding.

### Key Architecture Concepts

**Version 2 (Current)**: The system uses parallel execution with natural language input processing.

**Agent Flow**:
1. **Query Parser Node** (Gemini) - Converts natural language to structured context
2. **Parallel Analysis Node** - News, Technical, and Fundamental agents run simultaneously (3x faster than v1)
3. **Risk Agent** - Validates trade parameters and position sizing
4. **Synthesis Agent** (Gemini + Google Search) - Final decision with citations

**Critical**: Agents run in parallel using `ThreadPoolExecutor`. This is NOT parallelizable via multi-process due to API I/O-bound operations.

### State Management

The system uses LangGraph's `StateGraph` with `ForexAgentState` (defined in `graph/state.py`). State flows through:
- `user_query` (raw input) → `query_context` (parsed JSON) → agent results → final decision

**Backwards Compatibility**: The `pair` field is deprecated but maintained for compatibility.

## Common Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Then edit .env and add GOOGLE_AI_API_KEY from https://aistudio.google.com/app/apikey
```

### Running the System
```bash
# Run analysis with natural language
python main.py "Analyze gold trading"
python main.py "Should I buy Bitcoin?"
python main.py EUR/USD

# Run examples
python examples/basic_usage.py
python examples/natural_language.py
python examples/real_prices.py
```

### Testing
```bash
# Run basic validation tests
python test_basic.py

# Run specific test suites
python test_api_auth.py           # API authentication tests
python test_async_news.py         # Async news agent tests
python test_commodity_historical.py # Commodity price tests
python test_historical_price.py   # Historical price data tests
python test_price_api.py          # Price API integration tests

# Run all tests
pytest

# Run with verbose output
pytest -v
```

### Development Workflow
```bash
# Run a single test file
python test_basic.py

# Test the system interactively
python
>>> from system import ForexAgentSystem
>>> system = ForexAgentSystem()
>>> result = system.analyze("EUR/USD")
```

## Architecture Deep Dive

### LangGraph Workflow Structure

The workflow is defined in `graph/workflow.py` and uses these nodes:

1. **query_parser** (`graph/query_parser.py`):
   - Transforms natural language → structured JSON
   - Uses Gemini 2.5 Flash with low temperature (0.1)
   - Falls back to regex parsing if API fails
   - Extracts: pair, asset_type, timeframe, user_intent, risk_tolerance

2. **parallel_analysis** (`graph/parallel_nodes.py`):
   - Executes 3 agents simultaneously with `ThreadPoolExecutor`
   - News Agent (`agents/news_agent.py`) - Currently returns mock sentiment data
   - Technical Agent (`agents/technical_agent.py`) - Mock RSI, MACD, moving averages
   - Fundamental Agent (`agents/fundamental_agent.py`) - Mock GDP, interest rates, inflation

3. **risk** (`graph/nodes.py::risk_node`):
   - Uses RiskAgent (`agents/risk_agent.py`) with real LLM-powered analysis
   - Validates stop loss distance (10-100 pips)
   - Calculates position sizing based on account balance
   - Checks risk/reward ratio (minimum 1.5:1)
   - Returns `trade_approved: bool`

4. **synthesis** (`graph/nodes.py::synthesis_node`):
   - Only runs if risk approved (conditional routing)
   - Uses Gemini 2.5 Flash with Google Search grounding
   - Returns structured decision: BUY/SELL/WAIT
   - Includes reasoning, trade parameters, and source citations

### Conditional Routing

**After Risk Node**:
- `should_continue_after_risk()` checks if `risk_result.data.trade_approved == True`
- If False, workflow ends immediately with WAIT decision
- If True, proceeds to synthesis

### Price Service Integration

The `PriceService` class (`agents/price_service.py`) fetches real-time data:

- **Metal Price API** (metalpriceapi.com) - For commodities (XAU, XAG, XPT, XPD)
- **Forex Rate API** (forexrateapi.com) - For forex pairs and crypto

**Important**: Price APIs are optional. System falls back to mock data if keys not configured.

**API Authentication**: Uses query parameters (`?api_key=...`), NOT headers. See `test_api_auth.py` for details.

### Agent Implementation Pattern

All agents follow this pattern:
```python
class SomeAgent:
    def analyze(self, pair: str, query_context: Dict = None) -> Dict[str, Any]:
        try:
            # Perform analysis
            return {
                "success": True,
                "data": {...},
                "summary": "..."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

**Critical**: Agents must handle exceptions gracefully and return structured responses.

## File Organization

```
vibecode_claude/
├── agents/                      # Agent implementations
│   ├── news_agent.py           # News/sentiment (currently mock data)
│   ├── technical_agent.py      # Technical indicators (mock)
│   ├── fundamental_agent.py    # Economic fundamentals (mock)
│   ├── risk_agent.py          # Position sizing (LLM-powered)
│   └── price_service.py       # Real-time price fetching
│
├── graph/                      # LangGraph workflow components
│   ├── state.py               # State definition (ForexAgentState)
│   ├── workflow.py            # Workflow builder and compilation
│   ├── query_parser.py        # Natural language → JSON parser
│   ├── parallel_nodes.py      # Parallel agent execution
│   └── nodes.py               # Individual workflow nodes
│
├── examples/                   # Usage examples
│   ├── basic_usage.py         # Basic system usage
│   ├── natural_language.py    # Natural language query examples
│   └── real_prices.py         # Real price API integration
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # v1 → v2 evolution details
│   ├── SETUP.md              # Installation guide
│   ├── PRICE_API.md          # Price API documentation
│   ├── ASYNC_NEWS.md         # Async implementation notes
│   ├── API_AUTH_RESULTS.md   # API authentication research
│   └── AGENT_OPTIMIZATION.md # Agent optimization notes
│
├── test_*.py                  # Test files
├── system.py                  # Main ForexAgentSystem class
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
└── .env.example              # Environment template
```

## Environment Configuration

Required:
- `GOOGLE_AI_API_KEY` - Get from https://aistudio.google.com/app/apikey

Optional (for real price data):
- `METAL_PRICE_API_KEY` - From https://metalpriceapi.com/ (free tier available)
- `FOREX_RATE_API_KEY` - From https://forexrateapi.com/ (free tier available)
- `ACCOUNT_BALANCE` - Default: 10000.0
- `MAX_RISK_PER_TRADE` - Default: 0.02 (2%)

## Key Design Decisions

### Why LangGraph?
- Stateful workflow management
- Conditional routing based on risk assessment
- Easy to visualize and debug
- Better than sequential agent chains

### Why Parallel Execution?
- News, Technical, and Fundamental agents are independent
- 3x performance improvement (6s → 2s)
- Uses ThreadPoolExecutor (suitable for I/O-bound API calls)

### Why Mock Data in Most Agents?
This is a demonstration/educational project. The focus is on:
- Agent orchestration architecture
- LangGraph workflow patterns
- Gemini integration with Google Search grounding

Real data integration is intentionally left as a future enhancement (see README.md limitations).

### Why LLM-Powered Risk Agent?
The Risk Agent uses Gemini to:
- Make nuanced decisions about trade validity
- Provide detailed reasoning for rejections
- Adapt to different market conditions

This showcases LLM decision-making in a production-like workflow.

## Extending the System

### Adding a New Agent
1. Create agent class in `agents/new_agent.py`
2. Add node function in `graph/nodes.py` or `graph/parallel_nodes.py`
3. Update `ForexAgentState` in `graph/state.py` to include result field
4. Modify workflow in `graph/workflow.py` to include the new node
5. Update `system.py::_format_result()` to include agent results

### Adding Real Data Sources
Replace mock data in agents with real API calls:
- News: NewsAPI, Alpha Vantage
- Technical: Yahoo Finance, Alpha Vantage
- Fundamental: FRED API, Trading Economics

**Pattern**: Keep the same return structure (`{success, data, summary}`)

### Modifying Agent Prompts
Agent prompts for LLM-powered agents are in:
- Risk Agent: `agents/risk_agent.py::_build_analysis_prompt()`
- Synthesis Agent: `graph/nodes.py::synthesis_node()`

### Testing Changes
Always run `python test_basic.py` after making changes to verify the core workflow still works.

## Common Gotchas

1. **API Keys in Environment**: The system loads `.env` at startup. Changes to `.env` require restarting the system.

2. **Parallel vs Sequential**: Do NOT modify `parallel_analysis_node` to run sequentially without good reason. The 3x performance gain is critical.

3. **State Immutability**: LangGraph nodes return state updates, they don't modify state directly. Always return a dict with changed fields.

4. **Error Handling**: Agents should NEVER raise exceptions. They must return `{success: False, error: "..."}` to allow the workflow to continue.

5. **Query Context**: New code should use `query_context` from state, not just `pair`. The `pair` field is deprecated.

6. **Price API Authentication**: Use query parameters, NOT headers. See `test_api_auth.py` for correct implementation.

## Cost Considerations

Per analysis (~$0.095 total):
- Query Parser: ~$0.001 (Gemini 2.5 Flash, low tokens)
- Agent Execution: FREE (mock data, no API calls)
- Risk Agent: ~$0.002 (Gemini 2.5 Flash)
- Synthesis: ~$0.080 (Gemini 2.5 Flash + longer context)
- Google Search Grounding: ~$0.015 (included with Gemini)

100 analyses/day = ~$9.50/day = $285/month

**Optimization**: Use caching for repeated queries, implement rate limiting.

## Version History

**v1 (Initial)**: Sequential execution, exact pair format only
**v2 (Current)**: Parallel execution, natural language queries, 3x faster

See `docs/ARCHITECTURE.md` for detailed v1 → v2 evolution.
